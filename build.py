#!/usr/bin/env python3
"""Build Super Synth Lab Exquis Exhibit from versioned parts."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PARTS = SRC / "parts"
VENDOR = SRC / "vendor"
ROOT_INDEX = ROOT / "index.html"
DIST_DIR = ROOT / "dist"
DIST_INDEX = DIST_DIR / "index.html"
BUILD_COUNTER = ROOT / ".build-counter.json"
ROOT_SSLI_DIR = ROOT / "ssli"
DIST_SSLI_DIR = DIST_DIR / "ssli"
SSLI_ROOT = ROOT.parents[1] / "external" / "SuperSynthLabInstrument"
SSLI_SOURCE = SSLI_ROOT / "index.html"


@dataclass(frozen=True)
class TextPatch:
    name: str
    before: str
    after: str


SSLI_INDEX_PATCHES = [
    TextPatch(
        name="disable-stale-service-worker",
        before="<script>(function(){if('serviceWorker' in navigator){navigator.serviceWorker.register('sw.js').catch(function(e){console.warn('SW registration failed:',e);});}})();</script>",
        after="<script>console.info('[SSLI] service worker disabled for Exquis exhibit runtime');</script>",
    ),
    TextPatch(
        name="physical-fallback-pluck-deterministic-excitation-noise",
        before="""    this.delayLine.clear(); this.dcBlocker.clear(); this.loopFilter.clear();
    for (var bfc = 0; bfc < this.bodyFilters.length; bfc++) { this.bodyFilters[bfc].clear(); }
    var vel = (velocity || 100) / 127;
    var intPeriod = Math.ceil(period);
""",
        after="""    this.delayLine.clear(); this.dcBlocker.clear(); this.loopFilter.clear();
    for (var bfc = 0; bfc < this.bodyFilters.length; bfc++) { this.bodyFilters[bfc].clear(); }
    // Deterministic excitation keeps Playwright audio acceptance repeatable
    // while preserving the Karplus-Strong noise/displacement initial condition.
    // Original source: Karplus & Strong (1983), CMJ 7(2); LCG constants from
    // Numerical Recipes.
    var vel = (velocity || 100) / 127;
    var noiseSeed = ((Math.round(safeFreq * 1000) ^ (Math.round(velocity || 0) << 8) ^ Math.round(this.bodySize * 17)) >>> 0) || 1;
    var nextExcitationNoise = function() {
      noiseSeed = (1664525 * noiseSeed + 1013904223) >>> 0;
      return (noiseSeed / 2147483648) - 1;
    };
    var intPeriod = Math.ceil(period);
""",
    ),
    TextPatch(
        name="physical-fallback-pluck-loop-filter-brightness-range",
        before="""    this.delayLength = period - 0.5; // compensate for averaging filter group delay
    this.loopFilter.setCoeff(0.5 + (this.brightness / 100) * 0.45);
    this.maxDecay = Math.floor(this.sampleRate * (1 + (this.decayTime / 100) * 9));
""",
        after="""    this.delayLength = period - 0.5; // compensate for averaging filter group delay
    // Brightness maps to loop-filter loss, not a second heavy mute. Original
    // source: Smith, Physical Audio Signal Processing, frequency-dependent
    // decay via loop filters in string waveguides.
    this.loopFilter.setCoeff(0.82 + (this.brightness / 100) * 0.17);
    this.maxDecay = Math.floor(this.sampleRate * (1 + (this.decayTime / 100) * 9));
""",
    ),
    TextPatch(
        name="physical-fallback-picked-string-triangular-displacement-derivative",
        before="""    } else if (this.excitation === 'pick') {
      var half = Math.floor(intPeriod / 2);
      var safeHalf = half || 1;
      for (var i = 0; i < intPeriod; i++) {
        var env = i < half ? i / safeHalf : (intPeriod - i) / ((intPeriod - half) || 1);
        this.delayLine.write((env + (Math.random() * 2 - 1) * 0.15) * vel * 0.5);
      }
""",
        after="""    } else if (this.excitation === 'pick') {
      // A picked string starts from a triangular displacement at the pluck
      // point; excite the loop with the displacement delta so the pick
      // discontinuity is not smeared into a quiet fundamental-heavy arch.
      // Original source: Smith, Physical Audio Signal Processing, plucked
      // string initial conditions; Jaffe & Smith (1983), CMJ 7(2).
      var pick = Math.max(0.05, Math.min(0.95, this.pickPosition || 0.18));
      var previousDisplacement = 0;
      for (var i = 0; i < intPeriod; i++) {
        var x = i / Math.max(1, intPeriod - 1);
        var displacement = x < pick ? (x / pick) : ((1 - x) / (1 - pick));
        var displacementDelta = displacement - previousDisplacement;
        previousDisplacement = displacement;
        var pickNoise = nextExcitationNoise() * 0.04 * (1 - x);
        this.delayLine.write((displacementDelta * intPeriod * 0.18 + pickNoise) * vel);
      }
""",
    ),
    TextPatch(
        name="physical-fallback-pluck-noise-source-deterministic",
        before="""        this.delayLine.write((Math.random() * 2 - 1) * vel * 0.85);
""",
        after="""        this.delayLine.write(nextExcitationNoise() * vel * 0.85);
""",
    ),
    TextPatch(
        name="physical-fallback-pluck-output-tap-before-loop-damping",
        before="""    var dry = this.dcBlocker.process(filtered);
""",
        after="""    // Output is tapped from the delay-line string signal; the loop filter is
    // the feedback/damping path. Original source: Karplus & Strong (1983),
    // CMJ 7(2); Smith, Physical Audio Signal Processing, waveguide loop
    // filter placement.
    var dry = this.dcBlocker.process(delayed);
""",
    ),
    TextPatch(
        name="physical-fallback-pluck-decaytime-controls-t60-round-trip-loss",
        before="""    // Per-round-trip damping: the previous implementation used a per-sample
    // multiplier `1 - damping*0.003` which at high frequencies (short period)
    // compounds to complete silence in a few ms. We instead pick a per-round-trip
    // loss fraction and spread it across `period` samples so decay is
    // frequency-independent.
    var DAMPING_PER_RT_MAX_LOSS = 0.015;        // damping=100 -> 1.5%/round trip
    var dampingNorm = this.damping / 100;
    var lossPerRoundTrip = dampingNorm * DAMPING_PER_RT_MAX_LOSS;
    var minPeriodForDecay = 2.0;
    var safePeriod = period < minPeriodForDecay ? minPeriodForDecay : period;
    var guardedPeriod = safePeriod || 1;
    this._perSampleDecay = Math.pow(1.0 - lossPerRoundTrip, 1.0 / guardedPeriod);
""",
        after="""    // A delay-line sample is attenuated once per round trip, so decayTime must
    // map to that round-trip multiplier directly. Using a per-sample root here
    // makes plucked strings ring far longer than their requested T60.
    // Original source: Smith, Physical Audio Signal Processing, loop gain and
    // T60 relation g = 10^(-3P/(T60*Fs)) for delay length P.
    var dampingNorm = Math.max(0, Math.min(1, this.damping / 100));
    var decaySeconds = 0.45 + (Math.max(0, Math.min(100, this.decayTime)) / 100) * 2.2;
    var dampedDecaySeconds = decaySeconds * (1 - dampingNorm * 0.55);
    this._perSampleDecay = Math.pow(10, (-3 * Math.max(2, period)) / (dampedDecaySeconds * this.sampleRate));
""",
    ),
    TextPatch(
        name="physical-engine-export-live-note-pressure",
        before="""  function isReady() {
    return isWorkletReady || shouldUseFallback;
  }

  function getDefaultSettings() {
    return JSON.parse(JSON.stringify(DEFAULT_PHYSICAL_SETTINGS));
  }
""",
        after="""  function updateNotePressure(midi, pressure, instId) {
    if (instId === undefined) instId = 0;
    // Source for controller range: MIDI Association, MIDI 1.0 Detailed
    // Specification defines poly/channel pressure as one 7-bit value. SSLI
    // physical controls use 0-100 percent-style model parameters.
    var value = Math.max(0, Math.min(127, pressure || 0));
    var pct = value * (100 / 127);
    if (shouldUseFallback) {
      var voices = fallbackVoicesByInst[instId] || [];
      for (var i = 0; i < voices.length; i++) {
        var v = voices[i];
        if (!v.active || v.midiNote !== midi) continue;
        var model = v.currentModel;
        if (!model) continue;
        if (v.modelType === 'pluck') {
          model.brightness = pct;
          model.loopFilter.setCoeff(0.82 + (pct / 100) * 0.17);
        } else if (v.modelType === 'bow') {
          model.bowPressure = pct;
          model.bowTableSlope = 2.0 + (pct / 100) * 6.0;
          // Source: Smith, Physical Audio Signal Processing, bowed-string
          // waveguide junction; bow force affects nonlinear friction and the
          // drive applied at the bow/string contact point.
          model.maxVelocity = model.baseMaxVelocity * (0.1 + (pct / 100) * 3.0);
        } else if (v.modelType === 'blow') {
          model.breathPressure = pct;
        } else if (v.modelType === 'strike') {
          model.hardness = pct;
        }
      }
    } else if (physicalWorkletNodes[instId] && isWorkletReady) {
      physicalWorkletNodes[instId].port.postMessage({
        type: 'updateNotePressure',
        midiNote: midi,
        instId: instId,
        pressure: value
      });
    }
  }

  function isReady() {
    return isWorkletReady || shouldUseFallback;
  }

  function getDefaultSettings() {
    return JSON.parse(JSON.stringify(DEFAULT_PHYSICAL_SETTINGS));
  }
""",
    ),
    TextPatch(
        name="physical-engine-api-live-note-pressure",
        before="""  SL.physical = {
    init: init,
    isReady: isReady,

    noteOn: noteOn,
    noteOff: noteOff,
    allNotesOff: allNotesOff,
""",
        after="""  SL.physical = {
    init: init,
    isReady: isReady,

    noteOn: noteOn,
    noteOff: noteOff,
    updateNotePressure: updateNotePressure,
    allNotesOff: allNotesOff,
""",
    ),
    TextPatch(
        name="fm-engine-requires-instrument-output",
        before="""        if (inst && inst.masterOutput) {
          destination = inst.masterOutput;
          isDestinationResolved = true;
        } else if (audioContext) {
          destination = audioContext.destination;
          isDestinationResolved = true;
        }
""",
        after="""        if (inst && inst.masterOutput) {
          destination = inst.masterOutput;
          isDestinationResolved = true;
        }
""",
    ),
    TextPatch(
        name="fm-fallback-active-voice-makeup-gain",
        before="""        node.onaudioprocess = function(event) {
          var output = event.outputBuffer.getChannelData(0);
          for (var s = 0; s < output.length; s++) {
            var sample = 0;
            for (var vi = 0; vi < voices.length; vi++) {
              if (voices[vi].active) {
                // 0.18 scaling factor keeps multi-voice sum below clipping
                sample += voices[vi].process() * 0.18;
              }
            }
""",
        after="""        node.onaudioprocess = function(event) {
          var output = event.outputBuffer.getChannelData(0);
          var activeVoiceCount = 0;
          for (var ai = 0; ai < voices.length; ai++) {
            if (voices[ai].active) activeVoiceCount++;
          }
          // Active-voice makeup gain: for uncorrelated voices, summed RMS grows
          // as sqrt(N), so one-note lines should not keep the same reserve as
          // six-note chords. Original source: Smith, Physical Audio Signal
          // Processing, RMS power addition for uncorrelated signals.
          var voiceMakeupGain = Math.min(2.5, Math.sqrt(6 / Math.max(1, activeVoiceCount)));
          for (var s = 0; s < output.length; s++) {
            var sample = 0;
            for (var vi = 0; vi < voices.length; vi++) {
              if (voices[vi].active) {
                // 0.18 scaling factor keeps multi-voice sum below clipping.
                sample += voices[vi].process() * 0.18 * voiceMakeupGain;
              }
            }
""",
    ),
    TextPatch(
        name="subtractive-direct-midi-linear-velocity-amplitude",
        before="""    var velNorm = velocity / 127;
    var velCurved = velNorm * velNorm;
    var peak = velCurved * 0.12;
""",
        after="""    var velNorm = velocity / 127;
    // MIDI velocity is a 7-bit linear performance control; the user-selected
    // velocity curve is already applied before this direct WebAudio path.
    // Original source: MIDI 1.0 Detailed Specification, Note On velocity.
    var peak = velNorm * 0.12;
""",
    ),
    TextPatch(
        name="subtractive-sustained-linear-velocity-amplitude",
        before="""    var velLinear = (typeof velocity === 'number') ? (velocity / 127) : (100 / 127);
    var velGain = velLinear * velLinear;
""",
        after="""    var velLinear = (typeof velocity === 'number') ? (velocity / 127) : (100 / 127);
    // MIDI velocity is a 7-bit linear performance control; nonlinear response
    // belongs in the selected velocity curve, not in the engine gain law.
    // Original source: MIDI 1.0 Detailed Specification, Note On velocity.
    var velGain = velLinear;
""",
    ),
    TextPatch(
        name="subtractive-fallback-active-voice-rms-makeup",
        before="""    var peak = 0.12 * velGain;
    var attackTime = Math.max(0.003, adsr.a);
""",
        after="""    // 0.12 reserves four-voice headroom in the direct fallback path; restore
    // single-note level by the RMS power law as active voices change.
    // Original source: Smith, Physical Audio Signal Processing, RMS power addition.
    var activeVoiceCount = Math.max(1, activeOscs.size + 1);
    var peak = 0.12 * velGain * Math.sqrt(4 / activeVoiceCount);
    var attackTime = Math.max(0.003, adsr.a);
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-matrix-routing",
        before="""    var algo = ALGORITHMS[this.algorithm];
    if (!algo) return 0;
    var out = this.opOutputs;
    // Top-down traversal: Op6(index 5) first, Op1(index 0) last
    for (var i = 5; i >= 0; i--) {
      var modInput = 0;
      // Gather modulation from all operators routed to this one
      var mods = algo.modulations;
      for (var m = 0; m < mods.length; m++) {
        if (mods[m][1] === i) modInput += out[mods[m][0]];
      }
      // Feedback: one-sample delay of this operator's own output
      if (i === algo.feedbackOp) modInput += this.feedbackValue * this.feedbackLevel;
      out[i] = this.operators[i].process(modInput);
      if (i === algo.feedbackOp) this.feedbackValue = out[i];
    }
    var sample = 0;
    var carriers = algo.carriers;
    for (var c = 0; c < carriers.length; c++) sample += out[carriers[c]];
    // Normalize: divide by carrier count so loudness stays consistent
    // across algorithms regardless of how many carriers are active
    sample /= carriers.length;
""",
        after="""    // Source: Dexed Python package algorithms.py, decoded from DX7 algorithm
    // modulation matrices. Each mod entry is [target, source].
    var algo = DX7_ALGORITHM_MATRIX[(this.algorithm || 1) - 1];
    if (!algo) return 0;
    var out = this.opOutputs;
    for (var oi = 0; oi < 6; oi++) out[oi] = 0;
    var fb = algo.fb || [5, 5];
    var fbSource = fb[0];
    var fbTarget = fb[1];
    for (var i = 5; i >= 0; i--) {
      var modInput = 0;
      var mods = algo.mods;
      for (var m = 0; m < mods.length; m++) {
        if (mods[m][0] === i) modInput += out[mods[m][1]];
      }
      if (i === fbTarget) modInput += this.feedbackValue * this.feedbackLevel;
      out[i] = this.operators[i].process(modInput);
      if (i === fbSource) this.feedbackValue = out[i];
    }
    var sample = 0;
    var carriers = algo.carriers;
    for (var c = 0; c < carriers.length; c++) sample += out[carriers[c]];
    // Source: Dexed/msfa fm_core.cc opcode-based algorithm routing sums
    // carrier outputs; it does not divide audible carriers by carrier count.
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-routing-phase-units",
        before="""      out[i] = this.operators[i].process(modInput);
""",
        after="""      // Source: Dexed/msfa Sin::lookup phase units; fallback oscillator uses
      // radians internally, so convert routed phase cycles to radians here.
      out[i] = this.operators[i].process(modInput * 2 * Math.PI);
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-two-sample-feedback-state",
        before="""    this.feedbackValue = 0;
    this.instId = 0;
""",
        after="""    this.feedbackValue = 0;
    this.feedbackPair = [0, 0];
    this.instId = 0;
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-two-sample-feedback-reset",
        before="""    this.feedbackLevel = this.feedbackToScale(settings.feedback || 0);
    this.feedbackValue = 0;
    this.instId = settings.instId || 0;
""",
        after="""    this.feedbackLevel = this.feedbackToScale(settings.feedback || 0);
    this.feedbackValue = 0;
    this.feedbackPair[0] = 0;
    this.feedbackPair[1] = 0;
    this.instId = settings.instId || 0;
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-two-sample-feedback-routing",
        before="""      if (i === fbTarget) modInput += this.feedbackValue * this.feedbackLevel;
      // Source: Dexed/msfa Sin::lookup phase units; fallback oscillator uses
      // radians internally, so convert routed phase cycles to radians here.
      out[i] = this.operators[i].process(modInput * 2 * Math.PI);
      if (i === fbSource) this.feedbackValue = out[i];
""",
        after="""      var feedbackPair = this.feedbackPair;
      if (i === fbTarget) modInput += (feedbackPair[0] + feedbackPair[1]) * this.feedbackLevel;
      // Source: Dexed/msfa Sin::lookup phase units; fallback oscillator uses
      // radians internally, so convert routed phase cycles to radians here.
      out[i] = this.operators[i].process(modInput * 2 * Math.PI);
      if (i === fbSource) {
        feedbackPair[1] = feedbackPair[0];
        feedbackPair[0] = out[i];
      }
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-algorithm-matrix",
        before="""  // Minimal voice for fallback (runs on main thread)
  function FallbackOperator(sr) {
""",
        after="""  // Source: Dexed Python package algorithms.py, decoded from DX7 algorithm
  // modulation matrices; mods are [target, source] operator indices.
  var DX7_ALGORITHM_MATRIX = [{"carriers":[0,2],"mods":[[0,1],[2,3],[3,4],[4,5]],"fb":[5,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[3,4],[4,5]],"fb":[1,1]},{"carriers":[0,3],"mods":[[0,1],[1,2],[3,4],[4,5]],"fb":[5,5]},{"carriers":[0,3],"mods":[[0,1],[1,2],[3,4],[4,5]],"fb":[3,5]},{"carriers":[0,2,4],"mods":[[0,1],[2,3],[4,5]],"fb":[5,5]},{"carriers":[0,2,4],"mods":[[0,1],[2,3],[4,5]],"fb":[4,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[2,4],[4,5]],"fb":[5,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[2,4],[4,5]],"fb":[3,3]},{"carriers":[0,2],"mods":[[0,1],[2,3],[2,4],[4,5]],"fb":[1,1]},{"carriers":[0,3],"mods":[[0,1],[1,2],[3,4],[3,5]],"fb":[2,2]},{"carriers":[0,3],"mods":[[0,1],[1,2],[3,4],[3,5]],"fb":[5,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[2,4],[2,5]],"fb":[1,1]},{"carriers":[0,2],"mods":[[0,1],[2,3],[2,4],[2,5]],"fb":[5,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[3,4],[3,5]],"fb":[5,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[3,4],[3,5]],"fb":[1,1]},{"carriers":[0],"mods":[[0,1],[0,2],[0,4],[2,3],[4,5]],"fb":[5,5]},{"carriers":[0],"mods":[[0,1],[0,2],[0,4],[2,3],[4,5]],"fb":[1,1]},{"carriers":[0],"mods":[[0,1],[0,2],[0,3],[3,4],[4,5]],"fb":[2,2]},{"carriers":[0,3,4],"mods":[[0,1],[1,2],[3,5],[4,5]],"fb":[5,5]},{"carriers":[0,1,3],"mods":[[0,2],[1,2],[3,4],[3,5]],"fb":[2,2]},{"carriers":[0,1,3,4],"mods":[[0,2],[1,2],[3,5],[4,5]],"fb":[2,2]},{"carriers":[0,2,3,4],"mods":[[0,1],[2,5],[3,5],[4,5]],"fb":[5,5]},{"carriers":[0,1,3,4],"mods":[[1,2],[3,5],[4,5]],"fb":[5,5]},{"carriers":[0,1,2,3,4],"mods":[[2,5],[3,5],[4,5]],"fb":[5,5]},{"carriers":[0,1,2,3,4],"mods":[[3,5],[4,5]],"fb":[5,5]},{"carriers":[0,1,3],"mods":[[1,2],[3,4],[3,5]],"fb":[5,5]},{"carriers":[0,1,3],"mods":[[1,2],[3,4],[3,5]],"fb":[2,2]},{"carriers":[0,2,5],"mods":[[0,1],[2,3],[3,4]],"fb":[4,4]},{"carriers":[0,1,2,4],"mods":[[2,3],[4,5]],"fb":[5,5]},{"carriers":[0,1,2,5],"mods":[[2,3],[3,4]],"fb":[4,4]},{"carriers":[0,1,2,3,4],"mods":[[4,5]],"fb":[5,5]},{"carriers":[0,1,2,3,4,5],"mods":[],"fb":[5,5]}];
  var DX7_LEVEL_LUT = [0,5,9,13,17,20,23,25,27,29,31,33,35,37,39,41,42,43,45,46];
  var DX7_VELOCITY_DATA = [0,70,86,97,106,114,121,126,132,138,142,148,152,156,160,163,166,170,173,174,178,181,184,186,189,190,194,196,198,200,202,205,206,209,211,214,216,218,220,222,224,225,227,229,230,232,233,235,237,238,240,241,242,243,244,246,246,248,249,250,251,252,253,254];
  var DX7_EXP_SCALE_DATA = [0,1,2,3,4,5,6,7,8,9,11,14,16,19,23,27,33,39,47,56,66,80,94,110,126,142,158,174,190,206,222,238,250];
  var DX7_FEEDBACK_SCALE = [0];
  for (var dx7Fb = 1; dx7Fb <= 7; dx7Fb++) {
    // Source: Dexed/msfa fm_op_kernel.cc compute_fb() phase feedback shift.
    DX7_FEEDBACK_SCALE[dx7Fb] = Math.pow(2, dx7Fb - 9);
  }
  function dx7ScaleOutlevel(level) {
    level = Math.max(0, Math.min(99, Math.round(level || 0)));
    return level >= 20 ? 28 + level : (DX7_LEVEL_LUT[level] || 0);
  }
  function dx7ScaleVelocity(velocity, sensitivity) {
    var velValue = DX7_VELOCITY_DATA[Math.max(0, Math.min(127, Math.round(velocity || 0))) >> 1] - 239;
    return (((Math.max(0, Math.min(7, Math.round(sensitivity || 0))) * velValue + 7) >> 3) << 4);
  }
  function dx7EnvelopeLevelToLinear(level) {
    level = Math.max(0, Math.min(99, Math.round(level || 0)));
    if (level === 0) return 0;
    return ((dx7ScaleOutlevel(level) >> 1) << 6);
  }
  function dx7GainFromActualLevel(actualLevel) {
    actualLevel = Math.max(16, actualLevel);
    // Source: Dexed/msfa env.cc Exp2 gain followed by INT32_TO_FLOAT_SCALE:
    // actuallevel 3840 maps to unity final float gain.
    return Math.pow(2, (actualLevel - 3840) / 256);
  }
  function dx7ScaleCurve(group, depth, curve) {
    var scale;
    if (curve === 0 || curve === 3) scale = (group * depth * 329) >> 12;
    else scale = ((DX7_EXP_SCALE_DATA[Math.min(group, DX7_EXP_SCALE_DATA.length - 1)] || 0) * depth * 329) >> 15;
    return curve < 2 ? -scale : scale;
  }
  function dx7ScaleLevel(midiNote, breakPoint, leftDepth, rightDepth, leftCurve, rightCurve) {
    // Source: Dexed/msfa dx7note.cc ScaleLevel() and ScaleCurve().
    var offset = Math.round(midiNote || 0) - Math.round(breakPoint || 0) - 17;
    if (offset >= 0) return dx7ScaleCurve(Math.floor((offset + 1) / 3), rightDepth || 0, rightCurve || 0);
    return dx7ScaleCurve(Math.floor(-(offset - 1) / 3), leftDepth || 0, leftCurve || 0);
  }
  function dx7CombinedOperatorGain(envelopeLevel, operatorOutlevel) {
    // Source: Dexed/msfa env.cc combines EG level + operator outlevel before Exp2.
    return dx7GainFromActualLevel(envelopeLevel + operatorOutlevel - 4256);
  }
  function dx7KbdRateScale(midiNote, rateScaling) {
    // Source: Dexed/msfa dx7note.cc ScaleRate().
    var x = Math.min(31, Math.max(0, Math.floor(Math.max(0, Math.round(midiNote || 0)) / 3) - 7));
    return (Math.max(0, Math.min(7, Math.round(rateScaling || 0))) * x) >> 3;
  }
  function dx7FallbackOperatorGain(op, midiNote, velocity) {
    var outlevel = Math.min(127, dx7ScaleOutlevel(op.outputLevel) + dx7ScaleLevel(midiNote, op.breakPoint, op.leftDepth, op.rightDepth, op.leftCurve, op.rightCurve));
    outlevel = Math.max(0, (outlevel << 5) + dx7ScaleVelocity(velocity, op.velocitySens));
    // Source: Dexed/msfa dx7note.cc computes operator outlevel in the same
    // log-domain units later folded into env.cc actuallevel before Exp2.
    return outlevel;
  }

  // Minimal voice for fallback (runs on main thread)
  function FallbackOperator(sr) {
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-operator-source-fields",
        before="""    this.ratioCoarse = 1;
    this.ratioFine = 0;
    this.detune = 7;
    this.velocitySens = 0;
    this.velocityScale = 1;
""",
        after="""    this.ratioCoarse = 1;
    this.ratioFine = 0;
    this.frequencyMode = 0;
    this.detune = 7;
    this.velocitySens = 0;
    this.rateScaling = 0;
    this.breakPoint = 39;
    this.leftDepth = 0;
    this.rightDepth = 0;
    this.leftCurve = 0;
    this.rightCurve = 0;
    this.rateScalingOffset = 0;
    this.gainCurrent = 0;
    this.gainDelta = 0;
    this.gainSamplesLeft = 0;
    this.velocityScale = 1;
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-operator-source-params",
        before="""    if (p.ratioCoarse !== undefined) this.ratioCoarse = p.ratioCoarse;
    if (p.ratioFine !== undefined) this.ratioFine = p.ratioFine;
    if (p.level !== undefined) {
      this.outputLevel = p.level;
      // DX7 level-to-amplitude: approximately logarithmic.
      // Level 99 = 0 dB (full), each step down ~0.75 dB.
      // Formula: amplitude = 2^((level - 99) / 8)
      this.amplitude = p.level === 0 ? 0 : Math.pow(2, (p.level - 99) / 8);
    }
    if (p.detune !== undefined) this.detune = p.detune;
    if (p.velocitySens !== undefined) this.velocitySens = p.velocitySens;
    if (p.envelope) {
""",
        after="""    if (p.ratioCoarse !== undefined) this.ratioCoarse = p.ratioCoarse;
    if (p.ratioFine !== undefined) this.ratioFine = p.ratioFine;
    if (p.frequencyMode !== undefined) this.frequencyMode = p.frequencyMode;
    if (p.level !== undefined) {
      this.outputLevel = p.level;
      this.amplitude = dx7FallbackOperatorGain(this, 60, 127);
    }
    if (p.detune !== undefined) this.detune = p.detune;
    if (p.velocitySens !== undefined) this.velocitySens = p.velocitySens;
    if (p.rateScaling !== undefined) this.rateScaling = p.rateScaling;
    if (p.breakPoint !== undefined) this.breakPoint = p.breakPoint;
    if (p.leftDepth !== undefined) this.leftDepth = p.leftDepth;
    if (p.rightDepth !== undefined) this.rightDepth = p.rightDepth;
    if (p.leftCurve !== undefined) this.leftCurve = p.leftCurve;
    if (p.rightCurve !== undefined) this.rightCurve = p.rightCurve;
    if (p.envelope) {
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-keyon-gain-and-frequency",
        before="""  FallbackOperator.prototype.keyOn = function(noteFreq, velocity) {
    // Operator frequency = noteFreq * ratio * detuneMultiplier.
    // Coarse=0 is special: ratio becomes 0.5 (sub-octave).
    // Fine adds 0-99% on top of coarse (100 subdivisions between ratios).
    var ratio = this.ratioCoarse === 0 ? 0.5 : this.ratioCoarse;
    ratio *= (1 + this.ratioFine * 0.01);
    // Detune: value 7 = center (0 cents), range 0-14 = -7 to +7 cents
    var detuneCents = this.detune - 7;
    this.frequency = noteFreq * ratio * Math.pow(2, detuneCents / 1200);
    // Random initial phase prevents phase-locked constructive interference
    // between simultaneous voices (reduces harsh transients on chords)
    this.phase = Math.random();
    // Velocity sensitivity: sens=0 -> organ-like, sens=7 -> full dynamic range.
    // Linear crossfade between fixed amplitude (1.0) and velocity-scaled amplitude.
    var velNorm = velocity / 127;
    var sens = this.velocitySens / 7;
    this.velocityScale = 1 - sens + sens * velNorm;
""",
        after="""  FallbackOperator.prototype.keyOn = function(noteFreq, velocity, midiNote) {
    var ratio = this.ratioCoarse === 0 ? 0.5 : this.ratioCoarse;
    ratio *= (1 + this.ratioFine * 0.01);
    if (this.frequencyMode) {
      // Source: Dexed/msfa dx7note.cc fixed-frequency branch in osc_freq().
      this.frequency = Math.pow(10, (this.ratioCoarse & 3) + this.ratioFine / 100);
      if (this.detune > 7) {
        // Source: Dexed/msfa dx7note.cc fixed-frequency branch adds detune
        // in fixed-point frequency units only above center detune.
        this.frequency += 13457 * (this.detune - 7) / (1 << 24);
      }
    } else {
      this.frequency = noteFreq * ratio;
      if (this.detune !== 7) {
        // Source: Dexed/msfa dx7note.cc operator detune calculation:
        // detune is derived from the base note log frequency before applying
        // coarse/fine ratio multipliers.
        var logfreq = Math.log2(Math.max(1e-9, noteFreq)) * (1 << 24);
        var detuneRatio = 0.0209 * Math.exp(-0.396 * logfreq / (1 << 24)) / 7;
        var logOffset = detuneRatio * logfreq * (this.detune - 7);
        this.frequency += this.frequency * (Math.pow(2, logOffset / (1 << 24)) - 1);
      }
    }
    this.phase = Math.random();
    this.rateScalingOffset = dx7KbdRateScale(midiNote, this.rateScaling);
    this.amplitude = dx7FallbackOperatorGain(this, midiNote, velocity);
    this.gainCurrent = 0;
    this.gainDelta = 0;
    this.gainSamplesLeft = 0;
    this.velocityScale = 1;
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-envelope-qrate-and-log-gain",
        before="""  FallbackOperator.prototype.processEnv = function() {
    if (this.envFinished) return 0;
    var tgtRaw = this.envLevels[this.envStage];
    // Level mapping: power curve (x^2.5) approximates the DX7's
    // roughly logarithmic level perception
    var target = tgtRaw === 0 ? 0 : Math.pow(tgtRaw / 99, 2.5);
    var rate = this.envRates[this.envStage];
    // Convert rate to per-sample increment over 96 dB dynamic range
    var dbPerSec = 0.2819 * Math.pow(2, rate * 0.16);
    var inc = dbPerSec / (this.sampleRate * 96);
    if (this.envLevel < target) {
      this.envLevel += inc;
      if (this.envLevel >= target) { this.envLevel = target; this.advanceEnv(); }
    } else if (this.envLevel > target) {
      this.envLevel -= inc;
      if (this.envLevel <= target) { this.envLevel = target; this.advanceEnv(); }
    } else {
      this.advanceEnv();
    }
    return this.envLevel;
  };
""",
        after="""  FallbackOperator.prototype.dx7RateToIncrement = function(rate) {
    // Source: Dexed/msfa env.cc qrate/inc calculation.
    var qrate = Math.min(63, (((Math.max(0, Math.min(99, rate || 0)) * 41) >> 6) + (this.rateScalingOffset || 0)));
    var inc = (4 + (qrate & 3)) << (2 + 6 + (qrate >> 2));
    return (inc / 65536 / 64) * (44100 / this.sampleRate);
  };

  FallbackOperator.prototype.processEnv = function() {
    if (this.envFinished) return 0;
    // Source: Dexed/msfa env.cc Env::advance(): targetlevel is the DX7
    // envelope level plus operator outlevel before Exp2 gain conversion.
    var target = Math.max(16, dx7EnvelopeLevelToLinear(this.envLevels[this.envStage]) + this.amplitude - 4256);
    var inc = this.dx7RateToIncrement(this.envRates[this.envStage]) * 64;
    if (this.envLevel < target) {
      // Source: Dexed/msfa env.cc Env::getsample(): rising stages jump to
      // 1716 then advance nonlinearly by (((17 << 24) - level) >> 24) * inc.
      var jumpTarget = 1716;
      if (this.envLevel < jumpTarget) this.envLevel = jumpTarget;
      this.envLevel += (((17 * 16777216) - this.envLevel * 65536) / 16777216) * inc;
      if (this.envLevel >= target) { this.envLevel = target; this.advanceEnv(); }
    } else if (this.envLevel > target) {
      this.envLevel -= inc;
      if (this.envLevel <= target) { this.envLevel = target; this.advanceEnv(); }
    } else {
      this.advanceEnv();
    }
    return this.envLevel;
  };
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-ratio-fine-multiplicative-source-comment",
        before="""    var ratio = this.ratioCoarse === 0 ? 0.5 : this.ratioCoarse;
    ratio *= (1 + this.ratioFine * 0.01);
    if (this.frequencyMode) {
""",
        after="""    // Source: Dexed/msfa dx7note.cc osc_freq(): ratio mode is log-additive,
    // equivalent to coarse * (1 + fine/100), with coarse 0 as the DX7
    // half-frequency special case.
    var ratio = this.ratioCoarse === 0 ? 0.5 : this.ratioCoarse;
    ratio *= (1 + this.ratioFine * 0.01);
    if (this.frequencyMode) {
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-combined-log-domain-gain",
        before="""    var out = Math.sin(2 * Math.PI * this.phase + modInput);
    var env = this.processEnv();
    return out * env * this.amplitude * this.velocityScale;
""",
        after="""    var out = Math.sin(2 * Math.PI * this.phase + modInput);
    if (this.gainSamplesLeft <= 0) {
      var actualLevel = this.processEnv();
      var targetGain = dx7GainFromActualLevel(actualLevel);
      // Source: Dexed/msfa env.cc renders gains in N=64 sample blocks and
      // linearly interpolates dgain across the block.
      this.gainDelta = (targetGain - this.gainCurrent) / 64;
      this.gainSamplesLeft = 64;
    }
    this.gainCurrent += this.gainDelta;
    this.gainSamplesLeft--;
    return out * this.gainCurrent * this.velocityScale;
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-release-finished-actual-level",
        before="""      if (this.envStage === 3 && this.envLevel <= 0.0001) {
        this.envFinished = true;
        this.envLevel = 0;
      }
""",
        after="""      if (this.envStage === 3 && this.envLevel <= 16.1) {
        this.envFinished = true;
        this.envLevel = 16;
      }
""",
    ),
    TextPatch(
        name="fm-fallback-dx7-feedback-scale",
        before="""  FallbackVoice.prototype.feedbackToScale = function(fb) {
    if (fb === 0) return 0;
    return Math.PI * Math.pow(2, (fb - 7) / 2);
  };
""",
        after="""  FallbackVoice.prototype.feedbackToScale = function(fb) {
    fb = Math.max(0, Math.min(7, Math.round(fb || 0)));
    return DX7_FEEDBACK_SCALE[fb] || 0;
  };
""",
    ),
    TextPatch(
        name="fm-fallback-pass-midi-note-to-operators",
        before="""      this.operators[i].keyOn(freq, randomizedVel);
""",
        after="""      this.operators[i].keyOn(freq, randomizedVel, midi);
""",
    ),
]

SSLI_WORKLET_PATCHES = [
    TextPatch(
        name="fm-worklet-dx7-gain-lookup",
        before="""// Per-voice output scaling; keeps multi-voice sum below clipping
var VOICE_OUTPUT_GAIN = 0.18;
""",
        after="""// Per-voice output scaling; keeps multi-voice sum below clipping
var VOICE_OUTPUT_GAIN = 0.18;

// DX7/Dexed operator gain scaling.
// Original source: Dexed/msfa env.cc and dx7note.cc
// (scaleoutlevel(), ScaleVelocity(), and Exp2 log-domain gain).
// https://github.com/asb2m10/dexed/tree/master/Source/msfa
var DX7_LEVEL_LUT = [0, 5, 9, 13, 17, 20, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 42, 43, 45, 46];
var DX7_VELOCITY_DATA = [
  0, 70, 86, 97, 106, 114, 121, 126, 132, 138, 142, 148, 152, 156, 160, 163,
  166, 170, 173, 174, 178, 181, 184, 186, 189, 190, 194, 196, 198, 200, 202,
  205, 206, 209, 211, 214, 216, 218, 220, 222, 224, 225, 227, 229, 230, 232,
  233, 235, 237, 238, 240, 241, 242, 243, 244, 246, 246, 248, 249, 250, 251,
  252, 253, 254
];
var DX7_EXP_SCALE_DATA = [
  0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 14, 16, 19, 23, 27,
  33, 39, 47, 56, 66, 80, 94, 110, 126, 142, 158, 174,
  190, 206, 222, 238, 250
];

function dx7ScaleOutlevel(level) {
  level = Math.max(0, Math.min(99, Math.round(level || 0)));
  // Source: Dexed/msfa env.cc scaleoutlevel().
  if (level >= 20) return 28 + level;
  return DX7_LEVEL_LUT[level] || 0;
}

function dx7ScaleVelocity(velocity, sensitivity) {
  var clampedVelocity = Math.max(0, Math.min(127, Math.round(velocity || 0)));
  var sens = Math.max(0, Math.min(7, Math.round(sensitivity || 0)));
  // Source: Dexed/msfa dx7note.cc ScaleVelocity().
  var velValue = DX7_VELOCITY_DATA[clampedVelocity >> 1] - 239;
  return (((sens * velValue + 7) >> 3) << 4);
}

function dx7GainFromActualLevel(actualLevel) {
  actualLevel = Math.max(16, actualLevel);
  // Source: Dexed/msfa env.cc Exp2 gain followed by INT32_TO_FLOAT_SCALE:
  // actuallevel 3840 maps to unity final float gain.
  return Math.pow(2, (actualLevel - 3840) / 256);
}

function dx7EnvelopeLevelToLinear(level) {
  level = Math.max(0, Math.min(99, Math.round(level || 0)));
  if (level === 0) return 0;
  // Source: Dexed/msfa env.cc actuallevel envelope component.
  return ((dx7ScaleOutlevel(level) >> 1) << 6);
}

function dx7OperatorGain(level, velocity, sensitivity) {
  level = Math.max(0, Math.min(99, Math.round(level || 0)));
  if (level === 0) return 0;
  var outlevel = Math.min(127, dx7ScaleOutlevel(level));
  // Source: Dexed/msfa dx7note.cc: outlevel = scaleoutlevel(level) << 5 + ScaleVelocity().
  outlevel = (outlevel << 5) + dx7ScaleVelocity(velocity, sensitivity);
  return Math.max(0, outlevel);
}

function dx7ScaleCurve(group, depth, curve) {
  group = Math.max(0, Math.round(group || 0));
  depth = Math.max(0, Math.min(99, Math.round(depth || 0)));
  curve = Math.max(0, Math.min(3, Math.round(curve || 0)));
  var scale;
  if (curve === 0 || curve === 3) {
    scale = (group * depth * 329) >> 12;
  } else {
    var rawExp = DX7_EXP_SCALE_DATA[Math.min(group, DX7_EXP_SCALE_DATA.length - 1)];
    scale = (rawExp * depth * 329) >> 15;
  }
  if (curve < 2) scale = -scale;
  return scale;
}

function dx7ScaleLevel(midiNote, breakPoint, leftDepth, rightDepth, leftCurve, rightCurve) {
  // Source: Dexed/msfa dx7note.cc ScaleLevel() and ScaleCurve().
  var offset = Math.round(midiNote || 0) - Math.round(breakPoint || 0) - 17;
  if (offset >= 0) {
    return dx7ScaleCurve(Math.floor((offset + 1) / 3), rightDepth, rightCurve);
  }
  return dx7ScaleCurve(Math.floor(-(offset - 1) / 3), leftDepth, leftCurve);
}

function dx7CombinedOperatorGain(envelopeLevel, operatorOutlevel) {
  // Source: Dexed/msfa env.cc combines EG level + operator outlevel before Exp2.
  return dx7GainFromActualLevel(envelopeLevel + operatorOutlevel - 4256);
}

function dx7KbdRateScale(midiNote, rateScaling) {
  // Source: Dexed/msfa dx7note.cc ScaleRate().
  var x = Math.min(31, Math.max(0, Math.floor((midiNote || 0) / 3) - 7));
  return ((Math.max(0, Math.min(7, rateScaling || 0)) * x) >> 3);
}

// Source: Dexed/msfa fm_core.cc algorithm opcode table.
var DX7_ALGOS = [
  [0xc1,0x11,0x11,0x14,0x01,0x14],[0x01,0x11,0x11,0x14,0xc1,0x14],
  [0xc1,0x11,0x14,0x01,0x11,0x14],[0xc1,0x11,0x94,0x01,0x11,0x14],
  [0xc1,0x14,0x01,0x14,0x01,0x14],[0xc1,0x94,0x01,0x14,0x01,0x14],
  [0xc1,0x11,0x05,0x14,0x01,0x14],[0x01,0x11,0xc5,0x14,0x01,0x14],
  [0x01,0x11,0x05,0x14,0xc1,0x14],[0x01,0x05,0x14,0xc1,0x11,0x14],
  [0xc1,0x05,0x14,0x01,0x11,0x14],[0x01,0x05,0x05,0x14,0xc1,0x14],
  [0xc1,0x05,0x05,0x14,0x01,0x14],[0xc1,0x05,0x11,0x14,0x01,0x14],
  [0x01,0x05,0x11,0x14,0xc1,0x14],[0xc1,0x11,0x02,0x25,0x05,0x14],
  [0x01,0x11,0x02,0x25,0xc5,0x14],[0x01,0x11,0x11,0xc5,0x05,0x14],
  [0xc1,0x14,0x14,0x01,0x11,0x14],[0x01,0x05,0x14,0xc1,0x14,0x14],
  [0x01,0x14,0x14,0xc1,0x14,0x14],[0xc1,0x14,0x14,0x14,0x01,0x14],
  [0xc1,0x14,0x14,0x01,0x14,0x04],[0xc1,0x14,0x14,0x14,0x04,0x04],
  [0xc1,0x14,0x14,0x04,0x04,0x04],[0xc1,0x05,0x14,0x01,0x14,0x04],
  [0x01,0x05,0x14,0xc1,0x14,0x04],[0x04,0xc1,0x11,0x14,0x01,0x14],
  [0xc1,0x14,0x01,0x14,0x04,0x04],[0x04,0xc1,0x11,0x14,0x04,0x04],
  [0xc1,0x14,0x04,0x04,0x04,0x04],[0xc4,0x04,0x04,0x04,0x04,0x04]
];
var DX7_FEEDBACK_OP = [0,4,0,2,0,1,0,2,4,3,0,4,0,0,4,0,4,3,0,3,3,0,0,0,0,0,3,1,0,1,0,0];
var DX7_FEEDBACK_SCALE = [0];
for (var dx7Fb = 1; dx7Fb <= 7; dx7Fb++) {
  // Source: Dexed/msfa fm_op_kernel.cc compute_fb() phase feedback shift.
  DX7_FEEDBACK_SCALE[dx7Fb] = Math.pow(2, dx7Fb - 9);
}

// Source: Dexed Python package algorithms.py, decoded from DX7 algorithm
// modulation matrices; mods are [target, source] operator indices.
var DX7_ALGORITHM_MATRIX = [{"carriers":[0,2],"mods":[[0,1],[2,3],[3,4],[4,5]],"fb":[5,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[3,4],[4,5]],"fb":[1,1]},{"carriers":[0,3],"mods":[[0,1],[1,2],[3,4],[4,5]],"fb":[5,5]},{"carriers":[0,3],"mods":[[0,1],[1,2],[3,4],[4,5]],"fb":[3,5]},{"carriers":[0,2,4],"mods":[[0,1],[2,3],[4,5]],"fb":[5,5]},{"carriers":[0,2,4],"mods":[[0,1],[2,3],[4,5]],"fb":[4,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[2,4],[4,5]],"fb":[5,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[2,4],[4,5]],"fb":[3,3]},{"carriers":[0,2],"mods":[[0,1],[2,3],[2,4],[4,5]],"fb":[1,1]},{"carriers":[0,3],"mods":[[0,1],[1,2],[3,4],[3,5]],"fb":[2,2]},{"carriers":[0,3],"mods":[[0,1],[1,2],[3,4],[3,5]],"fb":[5,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[2,4],[2,5]],"fb":[1,1]},{"carriers":[0,2],"mods":[[0,1],[2,3],[2,4],[2,5]],"fb":[5,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[3,4],[3,5]],"fb":[5,5]},{"carriers":[0,2],"mods":[[0,1],[2,3],[3,4],[3,5]],"fb":[1,1]},{"carriers":[0],"mods":[[0,1],[0,2],[0,4],[2,3],[4,5]],"fb":[5,5]},{"carriers":[0],"mods":[[0,1],[0,2],[0,4],[2,3],[4,5]],"fb":[1,1]},{"carriers":[0],"mods":[[0,1],[0,2],[0,3],[3,4],[4,5]],"fb":[2,2]},{"carriers":[0,3,4],"mods":[[0,1],[1,2],[3,5],[4,5]],"fb":[5,5]},{"carriers":[0,1,3],"mods":[[0,2],[1,2],[3,4],[3,5]],"fb":[2,2]},{"carriers":[0,1,3,4],"mods":[[0,2],[1,2],[3,5],[4,5]],"fb":[2,2]},{"carriers":[0,2,3,4],"mods":[[0,1],[2,5],[3,5],[4,5]],"fb":[5,5]},{"carriers":[0,1,3,4],"mods":[[1,2],[3,5],[4,5]],"fb":[5,5]},{"carriers":[0,1,2,3,4],"mods":[[2,5],[3,5],[4,5]],"fb":[5,5]},{"carriers":[0,1,2,3,4],"mods":[[3,5],[4,5]],"fb":[5,5]},{"carriers":[0,1,3],"mods":[[1,2],[3,4],[3,5]],"fb":[5,5]},{"carriers":[0,1,3],"mods":[[1,2],[3,4],[3,5]],"fb":[2,2]},{"carriers":[0,2,5],"mods":[[0,1],[2,3],[3,4]],"fb":[4,4]},{"carriers":[0,1,2,4],"mods":[[2,3],[4,5]],"fb":[5,5]},{"carriers":[0,1,2,5],"mods":[[2,3],[3,4]],"fb":[4,4]},{"carriers":[0,1,2,3,4],"mods":[[4,5]],"fb":[5,5]},{"carriers":[0,1,2,3,4,5],"mods":[],"fb":[5,5]}];
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-detune-frequency",
        before="""    // Detune: +-7 cents, value 7 = center (one cent = 1/1200 of an octave)
    var detuneCents = (this.detune - 7);
    var detuneMultiplier = Math.pow(2, detuneCents / 1200);

    this.frequency = noteFreq * ratio * detuneMultiplier;
    // Pre-compute phase increment to avoid division in the hot loop
    this.phaseInc = this.frequency / this.sampleRate;
""",
        after="""    if (this.frequencyMode) {
      // Source: Dexed/msfa dx7note.cc fixed-frequency branch in osc_freq().
      this.frequency = Math.pow(10, (this.ratioCoarse & 3) + this.ratioFine / 100);
      // Source: Dexed/msfa dx7note.cc fixed-frequency branch applies detune
      // only above center detune.
      var fixedDetuneHz = this.detune > 7 ? 13457 * (this.detune - 7) / (1 << 24) : 0;
      this.phaseInc = (this.frequency + fixedDetuneHz) / this.sampleRate;
      return;
    }

    this.frequency = noteFreq * ratio;
    var detuneHz = 0;
    if (this.detune !== 7) {
      // Source: Dexed/msfa dx7note.cc operator detune calculation:
      // detune is derived from the base note log frequency before applying
      // coarse/fine ratio multipliers.
      var logfreq = Math.log2(Math.max(1e-9, noteFreq)) * (1 << 24);
      var detuneRatio = 0.0209 * Math.exp(-0.396 * logfreq / (1 << 24)) / 7;
      var logOffset = detuneRatio * logfreq * (this.detune - 7);
      detuneHz = this.frequency * (Math.pow(2, logOffset / (1 << 24)) - 1);
    }
    // Pre-compute phase increment to avoid division in the hot loop
    this.phaseInc = (this.frequency + detuneHz) / this.sampleRate;
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-envelope-level-curve",
        before="""  // Convert DX7 level (0-99) to linear amplitude.
  // Power curve (x^2.5) approximates the DX7's perceptual scaling:
  // level 99 -> 1.0, level 70 -> ~0.36, level 50 -> ~0.11
  dx7LevelToLinear(level) {
    if (level === 0) return 0;
    return Math.pow(level / 99, 2.5);
  }
""",
        after="""  // Convert DX7 level (0-99) to a Dexed-compatible linear gain.
  dx7LevelToLinear(level) {
    return dx7EnvelopeLevelToLinear(level);
  }
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-envelope-rate-scaling-state",
        before="""    this.cachedTarget = 0;     // Cached target level (linear)
    this.cachedIncrement = 0;  // Cached rate increment per sample
  }
""",
        after="""    this.cachedTarget = 0;     // Cached target level (linear)
    this.cachedIncrement = 0;  // Cached rate increment per sample
    this.rateScalingOffset = 0;
  }
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-envelope-qrate",
        before="""  // Convert DX7 rate (0-99) to linear increment per sample.
  // The DX7 envelope rate is exponential: each ~6 rate units doubles the speed.
  // Formula: rate_dB_per_sec = 0.2819 * 2^(rate * 0.16)
  // Normalized to 96 dB dynamic range (16-bit audio floor).
  // Rate 99 ~ 2ms full traverse; Rate 50 ~ 3 seconds; Rate 0 ~ minutes.
  dx7RateToIncrement(rate) {
    // rate in dB/s ~ 0.2819 * 2^(rate * 0.16)
    var dbPerSec = 0.2819 * Math.pow(2, rate * 0.16);
    var dbPerSample = dbPerSec / this.sampleRate;
    return dbPerSample / 96; // Normalize to 0..1 range (96 dB dynamic range)
  }
""",
        after="""  // Convert DX7 rate (0-99) to envelope increment using Dexed's qrate math.
  // Source: Dexed/msfa env.cc qrate/inc calculation.
  dx7RateToIncrement(rate) {
    var qrate = Math.min(63, (((Math.max(0, Math.min(99, rate || 0)) * 41) >> 6) + (this.rateScalingOffset || 0)));
    var inc = (4 + (qrate & 3)) << (2 + 6 + (qrate >> 2));
    return (inc / 65536 / 64) * (44100 / this.sampleRate);
  }
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-operator-level-curve",
        before="""  levelToAmplitude(level) {
    if (level === 0) return 0;
    return Math.pow(2, (level - 99) / 8);
  }
""",
        after="""  levelToAmplitude(level) {
    return dx7OperatorGain(level, 127, 0);
  }
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-operator-kls-state",
        before="""    this.ratioCoarse = 1;
    this.ratioFine = 0;
    this.detune = 7;       // 7 = center (0 cents offset)
    this.velocitySens = 0;
    this.rateScaling = 0;
    this.velocityScale = 1;
  }
""",
        after="""    this.ratioCoarse = 1;
    this.ratioFine = 0;
    this.frequencyMode = 0;
    this.detune = 7;       // 7 = center (0 cents offset)
    this.velocitySens = 0;
    this.rateScaling = 0;
    this.breakPoint = 39;
    this.leftDepth = 0;
    this.rightDepth = 0;
    this.leftCurve = 0;
    this.rightCurve = 0;
    this.velocityScale = 1;
  }
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-operator-kls-params",
        before="""    if (params.ratioCoarse !== undefined) this.ratioCoarse = params.ratioCoarse;
    if (params.ratioFine !== undefined) this.ratioFine = params.ratioFine;
    if (params.level !== undefined) {
      this.outputLevel = params.level;
      this.amplitude = this.levelToAmplitude(params.level);
    }
    if (params.detune !== undefined) this.detune = params.detune;
    if (params.velocitySens !== undefined) this.velocitySens = params.velocitySens;
    if (params.rateScaling !== undefined) this.rateScaling = params.rateScaling;
    if (params.envelope) {
""",
        after="""    if (params.ratioCoarse !== undefined) this.ratioCoarse = params.ratioCoarse;
    if (params.ratioFine !== undefined) this.ratioFine = params.ratioFine;
    if (params.frequencyMode !== undefined) this.frequencyMode = params.frequencyMode;
    if (params.level !== undefined) {
      this.outputLevel = params.level;
      this.amplitude = this.levelToAmplitude(params.level);
    }
    if (params.detune !== undefined) this.detune = params.detune;
    if (params.velocitySens !== undefined) this.velocitySens = params.velocitySens;
    if (params.rateScaling !== undefined) this.rateScaling = params.rateScaling;
    if (params.breakPoint !== undefined) this.breakPoint = params.breakPoint;
    if (params.leftDepth !== undefined) this.leftDepth = params.leftDepth;
    if (params.rightDepth !== undefined) this.rightDepth = params.rightDepth;
    if (params.leftCurve !== undefined) this.leftCurve = params.leftCurve;
    if (params.rightCurve !== undefined) this.rightCurve = params.rightCurve;
    if (params.envelope) {
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-velocity-scaling",
        before="""    // Velocity sensitivity: linear crossfade between full (1.0) and
    // velocity-proportional amplitude. sens=0 = organ (no dynamics),
    // sens=7 = full piano-like dynamics.
    // On a MODULATOR, velocity sensitivity controls brightness dynamics:
    // harder strikes = brighter tone (more modulation index).
    // This is critical for realistic electric piano patches.
    var velNorm = velocity / 127;
    var sens = this.velocitySens / 7;
    this.velocityScale = 1 - sens + sens * velNorm;

    this.envelope.keyOn();
""",
        after="""    var levelScaling = dx7ScaleLevel(
      midiNote,
      this.breakPoint,
      this.leftDepth,
      this.rightDepth,
      this.leftCurve,
      this.rightCurve
    );
    var scaledOutlevel = Math.min(127, dx7ScaleOutlevel(this.outputLevel) + levelScaling);
    // Source: Dexed/msfa dx7note.cc applies ScaleLevel() before shifting the
    // operator outlevel and adding ScaleVelocity().
    scaledOutlevel = Math.max(0, scaledOutlevel);
    this.amplitude = (scaledOutlevel << 5) + dx7ScaleVelocity(velocity, this.velocitySens);
    this.velocityScale = 1;

    this.envelope.keyOn();
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-combined-log-domain-gain",
        before="""    // Final output = sine * envelope * level * velocity
    var envLevel = this.envelope.process();
    return out * envLevel * this.amplitude * this.velocityScale;
""",
        after="""    // Final output = sine * combined DX7 log-domain operator gain.
    // Source: Dexed/msfa env.cc combines EG level and operator outlevel before Exp2.
    var envLevel = this.envelope.process();
    return out * dx7CombinedOperatorGain(envLevel, this.amplitude) * this.velocityScale;
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-operator-rate-scaling",
        before="""  keyOn(noteFreq, velocity) {
    this.computeFrequency(noteFreq);
""",
        after="""  keyOn(noteFreq, velocity, midiNote) {
    this.envelope.rateScalingOffset = dx7KbdRateScale(midiNote, this.rateScaling);
    this.computeFrequency(noteFreq);
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-pass-midi-note-to-operators",
        before="""      this.operators[i].keyOn(noteFreq, vel);
""",
        after="""      this.operators[i].keyOn(noteFreq, vel, midiNote);
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-feedback-scale",
        before="""  // Convert DX7 feedback level (0-7, 3 bits) to radians of self-modulation.
  // Feedback 0 = pure sine. Each step roughly doubles the modulation depth.
  // At feedback 3-4, the waveform approximates a sawtooth.
  // At feedback 7, the operator output approaches white noise.
  // The DX7 hardware used exactly this 3-bit exponential mapping.
  // Formula: scale = pi * 2^((fb - 7) / 2)
  feedbackToScale(fb) {
    // DX7 feedback 0-7 mapped to modulation scale
    // 0 = no feedback, 7 = maximum
    if (fb === 0) return 0;
    return Math.PI * Math.pow(2, (fb - 7) / 2);
  }
""",
        after="""  // Dexed/msfa feedback scale in phase cycles.
  // Source: Dexed/msfa fm_op_kernel.cc compute_fb().
  feedbackToScale(fb) {
    fb = Math.max(0, Math.min(7, Math.round(fb || 0)));
    return DX7_FEEDBACK_SCALE[fb] || 0;
  }
""",
    ),
    TextPatch(
        name="fm-worklet-dx7-bus-algorithm-routing",
        before="""    var algo = this.cachedAlgo;
    if (!algo) return 0;

    // Local variable aliases avoid repeated property lookups in the hot loop
    var ops = this.operators;
    var out = this.opOutputs;
    var opMod = this.opModSources;
    var fbOp = algo.feedbackOp;
    var fbLevel = this.feedbackLevel;
    var fbValue = this.feedbackValue;

    // Process operators top-down (6->1) so modulators compute before carriers
    for (var i = 5; i >= 0; i--) {
      var modInput = 0;

      // Sum modulation inputs from pre-compiled sources
      var sources = opMod[i];
      for (var m = 0; m < sources.length; m++) {
        modInput += out[sources[m]];
      }

      // Add feedback if this is the feedback operator
      if (i === fbOp) {
        modInput += fbValue * fbLevel;
      }

      // Process operator: sin(2*pi*f*t + modInput) * envelope * amplitude
      out[i] = ops[i].process(modInput);

      // Store for one-sample feedback delay
      if (i === fbOp) {
        fbValue = out[i];
      }
    }

    this.feedbackValue = fbValue;

    // Sum carrier outputs -- these are the operators that produce audible sound
    var sample = 0;
    var carriers = algo.carriers;
    for (var c = 0; c < carriers.length; c++) {
      sample += out[carriers[c]];
    }

    // Normalize by carrier count: Algorithm 32 (6 carriers) would be
    // 6x louder than Algorithm 7 (1 carrier) without this
    sample /= carriers.length;
""",
        after="""    // Source: Dexed Python package algorithms.py, decoded from DX7 algorithm
    // modulation matrices. Each mod entry is [target, source].
    var alg = DX7_ALGORITHM_MATRIX[(this.algorithm || 1) - 1];
    if (!alg) return 0;

    var ops = this.operators;
    var out = this.opOutputs;
    for (var oi = 0; oi < 6; oi++) out[oi] = 0;
    var feedbackPair = this.feedbackPair || [0, 0];
    this.feedbackPair = feedbackPair;
    var fbScale = this.feedbackLevel;
    var fb = alg.fb || [5, 5];
    var fbSource = fb[0];
    var fbTarget = fb[1];

    for (var i = 5; i >= 0; i--) {
      var modInput = 0;
      var mods = alg.mods;
      for (var mi = 0; mi < mods.length; mi++) {
        if (mods[mi][0] === i) modInput += out[mods[mi][1]];
      }
      if (i === fbTarget) {
        modInput += fbScale > 0 ? (feedbackPair[0] + feedbackPair[1]) * fbScale : 0;
      }

      // Source: Dexed/msfa Sin::lookup phase units; browser worklet uses radians.
      var opOut = ops[i].process(modInput * TWO_PI);
      out[i] = opOut;

      if (i === fbSource) {
        feedbackPair[1] = feedbackPair[0];
        feedbackPair[0] = opOut;
      }
    }

    var sample = 0;
    var carriers = alg.carriers;
    for (var c = 0; c < carriers.length; c++) sample += out[carriers[c]];
    // Source: Dexed/msfa fm_core.cc opcode-based algorithm routing sums
    // carrier outputs; it does not divide audible carriers by carrier count.
""",
    ),
    TextPatch(
        name="fm-worklet-remove-non-dx7-per-voice-soft-clipper",
        before="""    // Per-voice soft clipper for high feedback values.
    // At feedback >= 6, the operator can self-oscillate into extreme
    // amplitudes. tanh() provides smooth saturation that preserves
    // the fundamental while taming the peaks.
    var FB_SOFT_CLIP_THRESHOLD = 2.0;
    var TANH_SCALE = 0.8;
    var INV_TANH_SCALE = 1.0 / Math.tanh(TANH_SCALE);
    if (fbLevel > FB_SOFT_CLIP_THRESHOLD) {
      sample = Math.tanh(sample * TANH_SCALE) * INV_TANH_SCALE;
    }

""",
        after="""    // No per-voice feedback clipper here.
    // Original source: Dexed/msfa fm_op_kernel.cc compute_fb() applies feedback
    // through fixed-point phase scaling, not a tanh stage inside the voice.

""",
    ),
]

SSLI_PHYSICAL_WORKLET_PATCHES = [
    TextPatch(
        name="physical-worklet-pluck-output-family-scale",
        before="""var PLUCK_OUTPUT_SCALE = 3.0;
""",
        after="""// Karplus-Strong pluck excitation is an initial displacement/noise burst
// followed by loop damping; set the pluck-family output scale separately from
// sustained bowed/blown and struck modal models. Original source: Karplus &
// Strong (1983), CMJ 7(2); Jaffe & Smith (1983), CMJ 7(2).
var PLUCK_OUTPUT_SCALE = 9.0;
""",
    ),
    TextPatch(
        name="physical-worklet-deterministic-pluck-excitation-noise",
        before="""    // Excitation: fill delay line with shaped excitation
    var vel = (velocity || 100) / 127;
    var intPeriod = Math.ceil(period);
    var excLen = intPeriod;
""",
        after="""    // Excitation: fill delay line with shaped excitation. Karplus-Strong uses
    // noise as the initial string displacement; use deterministic pseudo-noise
    // per note so automated audio acceptance is repeatable while preserving
    // the noise-excited model. Original source: Karplus & Strong (1983), CMJ
    // 7(2); linear congruential PRNG constants from Numerical Recipes.
    var vel = (velocity || 100) / 127;
    var noiseSeed = ((Math.round(safeFreq * 1000) ^ (Math.round(velocity || 0) << 8) ^ Math.round(this.bodySize * 17)) >>> 0) || 1;
    var nextExcitationNoise = function() {
      noiseSeed = (1664525 * noiseSeed + 1013904223) >>> 0;
      return (noiseSeed / 2147483648) - 1;
    };
    var intPeriod = Math.ceil(period);
    var excLen = intPeriod;
""",
    ),
    TextPatch(
        name="physical-worklet-bow-pressure-slope-direction",
        before="""    // Bow pressure -> table slope (STK range ~2-8)
    this.bowTableSlope = 5.0 - (this.bowPressure / 100) * 3.0;
""",
        after="""    // Bow pressure -> table slope. Original source: Cook/Perry STK BowTable
    // exposes slope as the bow-pressure control; higher pressure stiffens the
    // nonlinear friction curve instead of reducing it.
    this.bowTableSlope = 2.0 + (this.bowPressure / 100) * 6.0;
""",
    ),
    TextPatch(
        name="physical-worklet-pluck-excitation-noise-source",
        before="""        var noise = (Math.random() * 2 - 1) * 0.15;
""",
        after="""        var noise = nextExcitationNoise() * 0.15;
""",
    ),
    TextPatch(
        name="physical-worklet-pluck-shaped-noise-source",
        before="""        var rawNoise = (Math.random() * 2 - 1);
""",
        after="""        var rawNoise = nextExcitationNoise();
""",
    ),
    TextPatch(
        name="physical-worklet-picked-string-triangular-displacement-derivative",
        before="""    } else if (this.excitation === 'pick') {
      // Triangle-ish pick excitation with half-Hann window
      var half = Math.floor(excLen / 2);
      var safeHalf = half || 1;
      for (var i = 0; i < excLen; i++) {
        var env = i < half ? i / safeHalf : (excLen - i) / ((excLen - half) || 1);
        // Half-Hann window for smoother onset
        var safeExcLenPick = excLen || 1;
        var hann = 0.5 * (1 - Math.cos(Math.PI * i / safeExcLenPick));
        var noise = nextExcitationNoise() * 0.15;
        this.delayLine.write((env + noise) * hann * vel * 0.5);
      }
""",
        after="""    } else if (this.excitation === 'pick') {
      // A picked string starts from a triangular displacement at the pluck
      // point; the delay-line excitation is the change in that displacement,
      // which preserves the pick discontinuity instead of smearing it into a
      // quiet fundamental-heavy arch. Original source: Smith, Physical Audio
      // Signal Processing, plucked string initial conditions; Jaffe & Smith
      // (1983), CMJ 7(2), pick-position filtering in extended Karplus-Strong.
      var pick = Math.max(0.05, Math.min(0.95, this.pickPosition || 0.5));
      var previousDisplacement = 0;
      for (var i = 0; i < excLen; i++) {
        var x = i / Math.max(1, excLen - 1);
        var displacement = x < pick ? (x / pick) : ((1 - x) / (1 - pick));
        var displacementDelta = displacement - previousDisplacement;
        previousDisplacement = displacement;
        var pickNoise = nextExcitationNoise() * 0.04 * (1 - x);
        this.delayLine.write((displacementDelta * excLen * 0.18 + pickNoise) * vel);
      }
""",
    ),
    TextPatch(
        name="physical-worklet-pluck-output-tap-before-loop-damping",
        before="""    // DC block
    var out = this.dcBlocker.process(filtered);
""",
        after="""    // Output is tapped from the delay-line string signal; the averaging and
    // loop filter belong in the feedback/damping path. Tapping only the
    // post-filter feedback sample over-damps picked transients. Original
    // source: Karplus & Strong (1983), CMJ 7(2); Smith, Physical Audio Signal
    // Processing, digital waveguide plucked-string loop filter placement.
    var out = this.dcBlocker.process(delayed);
""",
    ),
    TextPatch(
        name="physical-worklet-pick-position-independent-from-body-size",
        before="""    // Pick position for comb filtering (suppress harmonics at multiples of 1/pickPos)
    this.pickPosition = 0.13 + (this.bodySize / 100) * 0.35;
    this.pickDelay = Math.max(1, Math.floor(this.delayLength * this.pickPosition));
""",
        after="""    // Pick position is a string coordinate independent of resonating body size;
    // plucking nearer the bridge leaves more upper partial energy. Original
    // source: Jaffe & Smith (1983), CMJ 7(2), pick-position filtering in
    // extended Karplus-Strong.
    this.pickPosition = Math.max(0.05, Math.min(0.95, this.pickPosition));
    this.pickDelay = Math.max(1, Math.floor(this.delayLength * this.pickPosition));
""",
    ),
    TextPatch(
        name="physical-worklet-default-off-center-pick-position",
        before="""    this.pickPosition = 0.5;
    this.pickDelay = 0; // Pick position comb filter delay in samples
""",
        after="""    // Off-center plucking is the normal guitar/string case; a center pluck
    // suppresses even harmonics and sounds unnaturally dull unless explicitly
    // requested. Original source: Jaffe & Smith (1983), CMJ 7(2),
    // pick-position filtering in extended Karplus-Strong.
    this.pickPosition = 0.18;
    this.pickDelay = 0; // Pick position comb filter delay in samples
""",
    ),
    TextPatch(
        name="physical-worklet-pluck-settings-include-pick-position",
        before="""        this.pluck.bodySize = settings.bodySize != null ? settings.bodySize : 50;
        this.pluck.decayTime = settings.decayTime != null ? settings.decayTime : 70;
""",
        after="""        this.pluck.bodySize = settings.bodySize != null ? settings.bodySize : 50;
        this.pluck.pickPosition = settings.pickPosition != null ? settings.pickPosition : 0.18;
        this.pluck.decayTime = settings.decayTime != null ? settings.decayTime : 70;
""",
    ),
    TextPatch(
        name="physical-worklet-brightness-controls-ks-averaging-loss",
        before="""    // Two-point averaging (original KS algorithm) before loop filter
    var averaged = (delayed + this.prevSample) * 0.5;
    this.prevSample = delayed;
""",
        after="""    // Extended Karplus-Strong uses loop filtering to set frequency-dependent
    // decay. Keep the original two-sample averager as the dark end of the
    // brightness range instead of forcing every picked string through fixed
    // 0.5 high-frequency loss. Original source: Jaffe & Smith (1983), CMJ
    // 7(2); Smith, Physical Audio Signal Processing, loop-filter damping.
    var averageMix = 0.5 + (this.brightness / 100) * 0.45;
    var averaged = delayed * averageMix + this.prevSample * (1 - averageMix);
    this.prevSample = delayed;
""",
    ),
    TextPatch(
        name="physical-worklet-pluck-loop-filter-brightness-range",
        before="""    this.baseFilterCoeff = 0.5 + bright * 0.45;
    this.loopFilter.setCoeff(this.baseFilterCoeff);
""",
        after="""    // Brightness maps to loop-filter loss, not a second heavy mute. Plucked
    // nylon should retain upper partials while still damping faster than the
    // fundamental. Original source: Smith, Physical Audio Signal Processing,
    // frequency-dependent decay via loop filters in string waveguides.
    this.baseFilterCoeff = 0.82 + bright * 0.17;
    this.loopFilter.setCoeff(this.baseFilterCoeff);
""",
    ),
    TextPatch(
        name="physical-worklet-pluck-pressure-update-brightness-range",
        before="""            model.loopFilter.setCoeff(0.5 + (params.brightness / 100) * 0.45);
""",
        after="""            model.loopFilter.setCoeff(0.82 + (params.brightness / 100) * 0.17);
""",
    ),
    TextPatch(
        name="physical-worklet-marimba-tuned-bar-ratios",
        before="""      case 'wood':
        // Bar modes: Euler-Bernoulli beam theory gives f_n ~ n^2 for a
        // free-free bar. These measured ratios are from marimba bars.
        return [1, 2.76, 5.40, 8.93, 13.34, 18.64, 24.82, 31.87,
                39.81, 48.62, 58.31, 68.88, 80.33, 92.66, 105.86, 119.94];
""",
        after="""      case 'wood':
        // Tuned marimba bars are undercut so the first transverse modes sit
        // near 1:4:10 rather than the 1:2.76:5.40 free-free rectangular beam
        // ratios. Original source: Fletcher & Rossing, The Physics of
        // Musical Instruments, Ch. 19; Bretos et al. (1999) marimba-bar
        // measurements.
        return [1, 4.0, 10.0, 20.0, 33.0, 49.0, 68.0, 90.0,
                115.0, 143.0, 174.0, 208.0, 245.0, 285.0, 328.0, 374.0];
""",
    ),
    TextPatch(
        name="physical-worklet-marimba-mode-decay-ratios",
        before="""      // Frequency-dependent decay: higher modes decay faster (Q inversely proportional to mode number)
      var baseQ = 0.002 + (1 - this.decayTime / 100) * 0.02;
      var modeQ = baseQ * (1 + i * 0.15); // Higher modes get wider bandwidth = faster decay
""",
        after="""      // Frequency-dependent decay: higher marimba/bar modes decay faster than
      // the fundamental. Original source: Bork (1995), summarized in
      // Rossing-style marimba tuning references: modal decay is roughly
      // inverse to partial ratio for tuned 1:4:10 bars.
      var baseQ = 0.002 + (1 - this.decayTime / 100) * 0.02;
      var decayRatio = Math.max(1, ratios[i] || 1);
      var modeQ = baseQ * Math.sqrt(decayRatio) * (1 + i * 0.08);
""",
    ),
    TextPatch(
        name="physical-worklet-marimba-modal-output-headroom",
        before="""    this.outputScale = totalGain > 0 ? (0.8 / totalGain) : 1.0;
""",
        after="""    this.outputScale = totalGain > 0 ? (0.55 / totalGain) : 1.0;
    // Low bars radiate less efficiently than mid-register bars; scale struck
    // modal output by frequency below middle C instead of letting C3 dominate.
    // Original source: Fletcher & Rossing, The Physics of Musical Instruments,
    // Ch. 19, marimba bars and resonator radiation efficiency.
    this.outputScale *= Math.min(1, freq / 261.6255653005986);
""",
    ),
    TextPatch(
        name="physical-worklet-marimba-modal-amplitude-falloff",
        before="""      var spectralGain = Math.pow(hardnessFactor, i * 0.15);
      var distanceDecay = 1 / (1 + i * 0.3);

      this.modes[i].gain = vel * positionGain * spectralGain * distanceDecay;
""",
        after="""      var spectralGain = Math.pow(hardnessFactor, i * 0.15);
      // Modal excitation falls with mode number/frequency; total modal energy
      // is proportional to squared modal amplitudes. Original source: modal
      // summation energy orthogonality in Morse & Ingard, Theoretical
      // Acoustics, Ch. 6.
      var modalEnergyFalloff = 1 / Math.sqrt(Math.max(1, ratios[i] || 1));

      this.modes[i].gain = vel * positionGain * spectralGain * modalEnergyFalloff;
""",
    ),
    TextPatch(
        name="physical-worklet-polyphony-mix-gain",
        before="""    for (var s = 0; s < channel.length; s++) {
      var sample = 0;
      for (var a = 0; a < numActive; a++) {
        sample += voices[active[a]].process() * PHYS_VOICE_OUTPUT_GAIN;
      }
""",
        after="""    // Active-voice RMS makeup: summed uncorrelated voice power grows with N,
    // so a single pluck should not retain four-voice headroom. Original
    // source: Smith, Physical Audio Signal Processing, RMS power addition.
    var polyphonyMixGain = numActive > 4 ? 4 / numActive : Math.sqrt(4 / Math.max(1, numActive));
    for (var s = 0; s < channel.length; s++) {
      var sample = 0;
      for (var a = 0; a < numActive; a++) {
        sample += voices[active[a]].process() * PHYS_VOICE_OUTPUT_GAIN * polyphonyMixGain;
      }
""",
    ),
    TextPatch(
        name="physical-worklet-live-note-pressure-message",
        before="""      case 'updateParams':
        this.updateParams(data.instId, data.params);
        break;
""",
        after="""      case 'updateParams':
        this.updateParams(data.instId, data.params);
        break;

      case 'updateNotePressure':
        this.updateNotePressure(data.midiNote, data.instId, data.pressure);
        break;
""",
    ),
    TextPatch(
        name="physical-worklet-live-note-pressure-params",
        before="""  updateParams(instId, params) {
    // Update parameters on active voices for live tweaking
""",
        after="""  updateNotePressure(midiNote, instId, pressure) {
    // Source for controller range: MIDI Association, MIDI 1.0 Detailed
    // Specification defines poly/channel pressure as one 7-bit value. SSLI
    // physical controls use 0-100 percent-style model parameters.
    var value = Math.max(0, Math.min(127, pressure || 0));
    var pct = value * (100 / 127);
    for (var i = 0; i < this.maxVoices; i++) {
      var v = this.voices[i];
      if (!v.active || v.midiNote !== midiNote || v.instId !== instId) continue;
      var model = v.currentModel;
      if (!model) continue;
      if (v.modelType === 'pluck') {
        model.brightness = pct;
        model.loopFilter.setCoeff(0.82 + (pct / 100) * 0.17);
      } else if (v.modelType === 'bow') {
        model.bowPressure = pct;
        model.bowTableSlope = 2.0 + (pct / 100) * 6.0;
        // Source: Smith, Physical Audio Signal Processing, bowed-string
        // waveguide junction; bow force affects nonlinear friction and the
        // drive applied at the bow/string contact point.
        model.maxVelocity = model.baseMaxVelocity * (0.1 + (pct / 100) * 3.0);
      } else if (v.modelType === 'blow') {
        model.breathPressure = pct;
      } else if (v.modelType === 'strike') {
        model.hardness = pct;
      }
    }
  }

  updateParams(instId, params) {
    // Update parameters on active voices for live tweaking
""",
    ),
]

SSLI_FM_MIX_PATCHES = [
    TextPatch(
        name="fm-worklet-active-voice-makeup-gain",
        before="""    var voices = this.voices;
    var bufLen = channel.length;

    // Per-sample loop: sum all active voices, then soft-clip
    for (var s = 0; s < bufLen; s++) {
      var sample = 0;
      for (var v = 0; v < aviLen; v++) {
        sample += voices[avi[v]].process() * VOICE_OUTPUT_GAIN;
      }
""",
        after="""    var voices = this.voices;
    var bufLen = channel.length;
    // Active-voice makeup gain: for uncorrelated voices, summed RMS grows as
    // sqrt(N), so a one-note line should not keep the same headroom reserve as
    // a four-note chord. Original source: Smith, Physical Audio Signal
    // Processing, RMS power addition for uncorrelated signals.
    var voiceMakeupGain = Math.sqrt(4 / Math.max(1, aviLen));

    // Per-sample loop: sum all active voices, then soft-clip
    for (var s = 0; s < bufLen; s++) {
      var sample = 0;
      for (var v = 0; v < aviLen; v++) {
        sample += voices[avi[v]].process() * VOICE_OUTPUT_GAIN * voiceMakeupGain;
      }
""",
    ),
]

SSLI_SYNTH_WORKLET_PATCHES = [
    TextPatch(
        name="synth-worklet-active-voice-makeup-gain",
        before="""    // Generate audio for each active voice only
    for (var v = 0; v < aviLen; v++) {
      var voice = this.voices[avi[v]];
      if (voice.active) {
        for (var i = 0; i < blockSize; i++) {
          if (voice.startDelaySamples > 0) {
            voice.startDelaySamples--;
          } else {
            var sample = this.generateVoiceSample(voice, sampleDuration);
            // 0.12 master gain prevents clipping when many voices overlap.
            // With 64 voices at full amplitude, raw sum could reach ~64.0;
            // 0.12 brings the peak to ~7.7, which the soft clipper handles.
            channel[i] += sample * 0.12 * voice.velocityGain;
          }
        }
      }
    }
""",
        after="""    // Active-voice makeup gain: for uncorrelated voices, summed RMS grows as
    // sqrt(N), so a one-note line should not keep the same headroom reserve as
    // a four-note chord. Original source: Smith, Physical Audio Signal
    // Processing, RMS power addition for uncorrelated signals.
    var voiceMakeupGain = Math.sqrt(64 / Math.max(1, aviLen));

    // Generate audio for each active voice only
    for (var v = 0; v < aviLen; v++) {
      var voice = this.voices[avi[v]];
      if (voice.active) {
        for (var i = 0; i < blockSize; i++) {
          if (voice.startDelaySamples > 0) {
            voice.startDelaySamples--;
          } else {
            var sample = this.generateVoiceSample(voice, sampleDuration);
            // 0.12 ~= 1/sqrt(64) reserves 64-voice RMS headroom; voiceMakeupGain
            // restores normal single-note level and recedes as polyphony rises.
            channel[i] += sample * 0.12 * voice.velocityGain * voiceMakeupGain;
          }
        }
      }
    }
""",
    ),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def default_articulation(engine: str, preset: dict) -> dict:
    """Describe how simultaneous note-ons should be performed for this preset."""
    category = str(preset.get("category", ""))
    settings = preset.get("settings") or {}
    physical_model = str(settings.get("model") or settings.get("physicalSettings", {}).get("model") or "")
    if engine == "physical" and (category.lower() == "plucked" or physical_model == "pluck"):
        return {
            "family": "plucked",
            "onsetMode": "strum",
            "captureWindowMs": 18,
            "minInterOnsetMs": 11,
            "maxSpreadMs": 46,
            "order": "physical-low-to-high",
            "pressurePolicy": "onset-only"
        }
    if engine == "physical" and physical_model == "strike":
        return {
            "family": "struck",
            "onsetMode": "roll",
            "captureWindowMs": 10,
            "minInterOnsetMs": 5,
            "maxSpreadMs": 18,
            "order": "physical-low-to-high",
            "pressurePolicy": "capture-and-apply-at-onset"
        }
    return {
        "family": "sustained",
        "onsetMode": "immediate",
        "captureWindowMs": 0,
        "minInterOnsetMs": 0,
        "maxSpreadMs": 0,
        "order": "input",
        "pressurePolicy": "live"
    }


def with_articulation_defaults(engine: str, library: dict) -> dict:
    presets = []
    for preset in library.get("presets", []):
        enriched = dict(preset)
        enriched["articulation"] = dict(preset.get("articulation") or default_articulation(engine, preset))
        presets.append(enriched)
    return {**library, "presets": presets}


def next_build_info() -> dict:
    counter = 0
    if BUILD_COUNTER.exists():
        try:
            counter = int((json.loads(BUILD_COUNTER.read_text(encoding="utf-8")) or {}).get("build", 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            counter = 0
    build_number = counter + 1
    utc_dt = datetime.now(timezone.utc)
    local_dt = utc_dt.astimezone(ZoneInfo("America/New_York"))
    info = {
        "build": build_number,
        "version": f"Build {build_number}",
        "timestamp": local_dt.strftime("%Y-%m-%d %I:%M:%S %p ET"),
        "timestampUtc": utc_dt.isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    BUILD_COUNTER.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    return info


def build_bundle(metadata: dict) -> str:
    template = read_text(PARTS / "template.html")
    preset_dir = VENDOR / "ssli" / "presets"
    preset_libraries = {
        path.stem.replace("-presets", ""): with_articulation_defaults(path.stem.replace("-presets", ""), read_json(path))
        for path in sorted(preset_dir.glob("*-presets.json"))
    }
    ssli_vendor = {
        "source": "SuperSynthLabInstrument",
        "sourceFiles": [
            "shared/assets/constants.js",
            "shared/assets/data/scales-modes.json",
            "shared/assets/presets/*.json",
            "shared/assets/data/fx-presets.json"
        ],
        "scalesModes": read_json(VENDOR / "ssli" / "scales-modes.json"),
        "presetLibraries": preset_libraries,
        "fxPresets": read_json(VENDOR / "ssli" / "fx-presets.json")
    }
    bundle = template.replace("{{TITLE}}", metadata["name"])
    bundle = bundle.replace("{{CSS}}", read_text(PARTS / "styles.css"))
    bundle = bundle.replace("{{HTML}}", read_text(PARTS / "index.html"))
    bundle = bundle.replace("{{SSLI_VENDOR_JSON}}", json.dumps(ssli_vendor, separators=(",", ":")))
    bundle = bundle.replace("{{JS}}", read_text(PARTS / "app.js"))
    bundle = bundle.replace("{{BUILD_VERSION}}", metadata["buildVersion"])
    bundle = bundle.replace("{{BUILD_TIMESTAMP}}", metadata["buildTimestamp"])
    bundle = bundle.replace("{{BUILD_TIMESTAMP_UTC}}", metadata["buildTimestampUtc"])
    return bundle


def sync_ssli_runtime(target: Path) -> None:
    target.mkdir(exist_ok=True)
    if SSLI_SOURCE.exists():
        shutil.copyfile(SSLI_SOURCE, target / "index.html")
        ssli_assets = SSLI_ROOT / "assets"
        if ssli_assets.exists():
            shutil.copytree(ssli_assets, target / "assets", dirs_exist_ok=True)
        for support_file in ("manifest.json", "sw.js", "logo.png"):
            source_file = SSLI_ROOT / support_file
            if source_file.exists():
                shutil.copyfile(source_file, target / support_file)
    elif target.resolve() != ROOT_SSLI_DIR.resolve() and ROOT_SSLI_DIR.exists() and (ROOT_SSLI_DIR / "index.html").exists():
        shutil.copytree(ROOT_SSLI_DIR, target, dirs_exist_ok=True)
    patch_ssli_runtime(target)


def patch_ssli_runtime(target: Path) -> None:
    """Apply exhibit-local SSLI runtime patches that are covered by tests."""
    index = target / "index.html"
    if index.exists():
        text = index.read_text(encoding="utf-8")
        patched = apply_required_text_patches(text, SSLI_INDEX_PATCHES, index)
        patched = apply_required_text_patches(patched, SSLI_PHYSICAL_WORKLET_PATCHES, index)
        patched = apply_required_text_patches(patched, SSLI_FM_MIX_PATCHES, index)
        patched = apply_required_text_patches(patched, SSLI_SYNTH_WORKLET_PATCHES, index)
        if patched != text:
            index.write_text(patched, encoding="utf-8")
    worklet = target / "assets" / "fm-worklet.js"
    if worklet.exists():
        text = worklet.read_text(encoding="utf-8")
        patched = apply_required_text_patches(text, SSLI_WORKLET_PATCHES, worklet)
        patched = apply_required_text_patches(patched, SSLI_FM_MIX_PATCHES, worklet)
        if patched != text:
            worklet.write_text(patched, encoding="utf-8")
    synth_worklet = target / "assets" / "synth-worklet.js"
    if synth_worklet.exists():
        text = synth_worklet.read_text(encoding="utf-8")
        patched = apply_required_text_patches(text, SSLI_SYNTH_WORKLET_PATCHES, synth_worklet)
        if patched != text:
            synth_worklet.write_text(patched, encoding="utf-8")
    physical_worklet = target / "assets" / "physical-worklet.js"
    if physical_worklet.exists():
        text = physical_worklet.read_text(encoding="utf-8")
        patched = apply_required_text_patches(text, SSLI_PHYSICAL_WORKLET_PATCHES, physical_worklet)
        if patched != text:
            physical_worklet.write_text(patched, encoding="utf-8")


def apply_required_text_patches(text: str, patches: list[TextPatch], target: Path) -> str:
    """Apply idempotent text patches and fail loudly when upstream drift breaks one."""
    patched = text
    for patch in patches:
        has_before = patch.before in patched
        has_after = patch.after in patched
        if not has_before and not has_after:
            raise RuntimeError(f"Missing SSLI runtime patch target '{patch.name}' in {target}")
        if has_before:
            patched = patched.replace(patch.before, patch.after)
    return patched


def build() -> dict:
    metadata_src = read_json(SRC / "metadata.json")
    build_info = next_build_info()
    metadata_src["buildNumber"] = build_info["build"]
    metadata_src["buildVersion"] = build_info["version"]
    metadata_src["buildTimestamp"] = build_info["timestamp"]
    metadata_src["buildTimestampUtc"] = build_info["timestampUtc"]
    bundle = build_bundle(metadata_src)
    DIST_DIR.mkdir(exist_ok=True)
    ROOT_INDEX.write_text(bundle, encoding="utf-8")
    DIST_INDEX.write_text(bundle, encoding="utf-8")
    sync_ssli_runtime(ROOT_SSLI_DIR)
    sync_ssli_runtime(DIST_SSLI_DIR)
    return {
        "name": metadata_src["name"],
        "buildNumber": metadata_src["buildNumber"],
        "buildVersion": metadata_src["buildVersion"],
        "buildTimestamp": metadata_src["buildTimestamp"],
        "buildTimestampUtc": metadata_src["buildTimestampUtc"],
        "rootIndex": str(ROOT_INDEX),
        "distIndex": str(DIST_INDEX),
        "ssliRuntime": str(ROOT_SSLI_DIR),
    }


if __name__ == "__main__":
    result = build()
    print(f"Built {result['rootIndex']}")
    print(f"Built {result['distIndex']}")
    print(f"Synced SSLI runtime: {result['ssliRuntime']}")
