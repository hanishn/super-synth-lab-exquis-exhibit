(function() {
  'use strict';

  var SSLI_VENDOR = window.SSLI_VENDOR || {};
  var SSLI_MODES = SSLI_VENDOR.scalesModes || {};
  var SSLI_PRESETS = SSLI_VENDOR.presetLibraries || {};
  var SSLI_FX_PRESETS = SSLI_VENDOR.fxPresets || {};
  var NOTES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  var NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'];
  var FLAT_KEY_ROOTS = [5, 10, 3, 8, 1, 6];
  var TONICS = [
    { name: 'C', pc: 0 }, { name: 'Db', pc: 1 }, { name: 'D', pc: 2 },
    { name: 'Eb', pc: 3 }, { name: 'E', pc: 4 }, { name: 'F', pc: 5 },
    { name: 'F#', pc: 6 }, { name: 'G', pc: 7 }, { name: 'Ab', pc: 8 },
    { name: 'A', pc: 9 }, { name: 'Bb', pc: 10 }, { name: 'B', pc: 11 }
  ];
  var SCALE_KEYS = ['ionian', 'aeolian', 'penta_min', 'penta_maj', 'chromatic', 'dorian', 'mixolydian', 'blues'];
  var NOTE_PC = { 'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11 };
  // Official Exquis-style printed note grid, top to bottom. The hardware is
  // 61 keys in alternating 6/5 rows; live MIDI calibration supplies exact MIDI.
  var EXQUIS_NOTE_ROWS = [
    ['D', 'D#', 'E', 'F', 'F#', 'G'],
    ['B', 'C', 'C#', 'D', 'D#'],
    ['G', 'G#', 'A', 'A#', 'B', 'C'],
    ['E', 'F', 'F#', 'G', 'G#'],
    ['C', 'C#', 'D', 'D#', 'E', 'F'],
    ['A', 'A#', 'B', 'C', 'C#'],
    ['F', 'F#', 'G', 'G#', 'A', 'A#'],
    ['D', 'D#', 'E', 'F', 'F#'],
    ['A#', 'B', 'C', 'C#', 'D', 'D#'],
    ['G', 'G#', 'A', 'A#', 'B'],
    ['D#', 'E', 'F', 'F#', 'G', 'G#']
  ];
  var DEFAULT_C_MAJOR_LED_IDS = [
    'r0c2', 'r0c3',
    'r1c1', 'r1c3',
    'r2c2', 'r2c4',
    'r3c1', 'r3c3',
    'r4c2', 'r4c4',
    'r5c2', 'r5c3',
    'r6c2', 'r6c4',
    'r7c2', 'r7c3',
    'r8c2', 'r8c4',
    'r9c2', 'r9c4',
    'r10c2', 'r10c4'
  ];
  var STRATEGIES = [
    {
      id: 'ladder4',
      name: '4-finger ladder',
      leftFingers: [5, 4, 3, 2, 5, 4, 3, 2],
      rightFingers: [2, 3, 4, 5, 2, 3, 4, 5],
      rule: 'Use 5-4-3-2, shift the hand, then repeat. Keep the thumb quiet at first.'
    },
    {
      id: 'thumb_assist',
      name: 'Thumb-assisted',
      leftFingers: [5, 4, 3, 2, 1, 3, 2, 1],
      rightFingers: [1, 2, 3, 4, 5, 3, 4, 5],
      rule: 'Use the thumb for the upper turn only. Avoid piano-style thumb-under as your default.'
    },
    {
      id: 'position_shift',
      name: 'Position shift',
      leftFingers: [4, 3, 2, 1, 4, 3, 2, 1],
      rightFingers: [1, 2, 3, 4, 1, 2, 3, 4],
      rule: 'Use 4-3-2-1 in compact positions and move the whole hand between groups.'
    }
  ];
  var ROW_COUNTS = [6, 5, 6, 5, 6, 5, 6, 5, 6, 5, 6];
  var CELL_W = 48.49742261192856;
  var CELL_H = 56;
  var ROW_STEP = 42;
  var VERTICAL_ROW_STEP = 42;
  var SURFACE_W = 470;
  var SURFACE_H = 690;
  var SURFACE_HORIZONTAL_W = 620;
  var LOCAL_MASTER_GAIN = 2.6;
  var SSLI_PRACTICE_OUTPUT_GAIN = 4;
  var EXQUIS_BOTTOM_LEFT_MIDI = 27;
  var VERTICAL_THIRD = 4;
  var audioCtx = null;
  var audioAnalyser = null;
  var fxInput = null;
  var fxOutput = null;
  var fxNodes = [];
  var audioScopeTimer = null;
  var audioScopeData = null;
  var heldScopeData = null;
  var heldScopePeak = 0;
  var heldScopeUntil = 0;
  var currentPath = [];
  var midiAccess = null;
  var midiInput = null;
  var midiHitTimer = null;
  var midiActivityTimer = null;
  var resizeTimer = null;
  var logs = [];
  var midiVoices = {};
  var lastAppliedSsliPresetKey = '';
  var MIDI_VOICE_BUDGET = 12;
  var state = {
    tonicPc: 0,
    rootCellId: '',
    hand: 'left',
    scaleId: 'ionian',
    strategyId: 'ladder4',
    view: 'practice',
    tone: 'soft_wurli',
    soundPresetId: 'subtractive::Wurlitzer EP',
    soundEngine: 'subtractive',
    soundCategory: 'Keys',
    fxPresetId: 'dry',
    fxCategory: 'Clean / Natural',
    fxDirty: false,
    filterType: 'lowpass',
    filterCutoff: 2200,
    filterResonance: 0.8,
    filterDirty: false,
    orientation: 'horizontal',
    rotation: 0,
    step: 0,
    lastMidi: null,
    activeMidiCellId: '',
    activeMidiPc: null,
    lastMidiCellId: '',
    lastMidiPc: null,
    rawMidiFlash: false,
    lastMidiAt: 0,
    midiInputs: [],
    selectedMidiId: '',
    midiStatus: 'MIDI is off.',
    midiActivity: 'Activity: none',
    audioStatus: 'Audio: locked until Play/Test.',
    feedback: 'Enable MIDI to compare the physical Exquis against the current target.',
    feedbackKind: 'neutral',
    autoAdvance: true,
    heldNotes: {},
    channelNotes: {},
    correctCount: 0,
    missCount: 0,
    streak: 0,
    calibrated: {},
    mismatched: {}
  };
  var els = {};

  function logEvent(kind, message) {
    var stamp = new Date().toLocaleTimeString();
    logs.push(stamp + ' [' + kind + '] ' + message);
    if (logs.length > 120) logs.shift();
    if (els.diagnosticLog) {
      els.diagnosticLog.textContent = logs.join('\n') || 'Ready.';
      els.diagnosticLog.scrollTop = els.diagnosticLog.scrollHeight;
    }
  }

  function resetVisualMidi() {
    state.activeMidiCellId = '';
    state.activeMidiPc = null;
    state.lastMidiCellId = '';
    state.lastMidiPc = null;
    state.rawMidiFlash = false;
    state.heldNotes = {};
    state.channelNotes = {};
    Object.keys(midiVoices).forEach(function(key) {
      releaseMidiVoice(key, true);
    });
    if (midiHitTimer) window.clearTimeout(midiHitTimer);
  }

  function voiceKey(channel, midi) {
    return String(channel) + ':' + String(midi);
  }

  function mod(n, m) {
    return ((n % m) + m) % m;
  }

  function noteName(midi) {
    var names = FLAT_KEY_ROOTS.indexOf(state.tonicPc) >= 0 ? NOTES_FLAT : NOTES_SHARP;
    return names[mod(midi, 12)];
  }

  function octave(midi) {
    return Math.floor(midi / 12) - 1;
  }

  function getScale() {
    var scale = SSLI_MODES[state.scaleId] || SSLI_MODES.ionian;
    return {
      id: state.scaleId,
      name: scale && scale.name ? scale.name : 'Major',
      intervals: scale && scale.scale ? scale.scale : [0, 2, 4, 5, 7, 9, 11]
    };
  }

  function getStrategy() {
    for (var i = 0; i < STRATEGIES.length; i++) {
      if (STRATEGIES[i].id === state.strategyId) return STRATEGIES[i];
    }
    return STRATEGIES[0];
  }

  function getStrategyFingers(strategy) {
    return state.hand === 'right' ? strategy.rightFingers : strategy.leftFingers;
  }

  function getHandRule(strategy) {
    if (state.hand === 'right') {
      return strategy.rule.replace('5-4-3-2', '2-3-4-5').replace('4-3-2-1', '1-2-3-4');
    }
    return strategy.rule;
  }

  function getSoundPresetOptions() {
    var options = [];
    Object.keys(SSLI_PRESETS).sort().forEach(function(family) {
      var library = SSLI_PRESETS[family];
      var presets = library && library.presets ? library.presets : [];
      for (var i = 0; i < presets.length; i++) {
        options.push({
          id: family + '::' + presets[i].name,
          family: family,
          preset: presets[i],
          label: family + ' / ' + (presets[i].category || 'Preset') + ' / ' + presets[i].name
        });
      }
    });
    return options;
  }

  function getSoundEngines() {
    var host = getSsliHost();
    var SL = host && host.SynthLab;
    if (SL && SL.presets && SL.presets.getEngines) {
      return SL.presets.getEngines();
    }
    return Object.keys(SSLI_PRESETS).sort();
  }

  function getSoundCategories(engine) {
    var host = getSsliHost();
    var SL = host && host.SynthLab;
    if (SL && SL.presets && SL.presets.getCategoriesForEngine) {
      return SL.presets.getCategoriesForEngine(getSsliEngineDisplayName(engine, SL));
    }
    var seen = {};
    var library = SSLI_PRESETS[engine] || {};
    var presets = library.presets || [];
    for (var i = 0; i < presets.length; i++) {
      seen[presets[i].category || 'Preset'] = true;
    }
    return Object.keys(seen).sort();
  }

  function getSoundPresetsFor(engine, category) {
    var host = getSsliHost();
    var SL = host && host.SynthLab;
    if (SL && SL.presets && SL.presets.getPresetsForEngineCategory) {
      return SL.presets.getPresetsForEngineCategory(getSsliEngineDisplayName(engine, SL), category) || [];
    }
    var library = SSLI_PRESETS[engine] || {};
    var presets = library.presets || [];
    return presets.filter(function(preset) {
      return (preset.category || 'Preset') === category;
    }).sort(function(a, b) {
      return a.name.localeCompare(b.name);
    });
  }

  function syncSoundSelectorsFromPreset() {
    var selected = getCurrentSoundPreset();
    if (!selected) return;
    state.soundEngine = selected.family;
    state.soundCategory = selected.preset.category || 'Preset';
  }

  function getCurrentSoundPreset() {
    var host = getSsliHost();
    var SL = host && host.SynthLab;
    if (SL && SL.presets && SL.presets.getPresetsForEngineCategory) {
      var engineName = getSsliEngineDisplayName(state.soundEngine, SL);
      var category = state.soundCategory || '';
      var presetName = state.soundPresetId && state.soundPresetId.indexOf('::') >= 0 ? state.soundPresetId.split('::').slice(1).join('::') : '';
      var categories = SL.presets.getCategoriesForEngine ? SL.presets.getCategoriesForEngine(engineName) : [];
      if (categories.indexOf(category) < 0) category = categories[0] || category;
      var runtimePresets = SL.presets.getPresetsForEngineCategory(engineName, category) || [];
      var runtimePreset = runtimePresets[0] || null;
      for (var runtimeIndex = 0; runtimeIndex < runtimePresets.length; runtimeIndex++) {
        if (runtimePresets[runtimeIndex] && runtimePresets[runtimeIndex].name === presetName) {
          runtimePreset = runtimePresets[runtimeIndex];
          break;
        }
      }
      if (runtimePreset) {
        state.soundEngine = engineName;
        state.soundCategory = runtimePreset.category || category || 'Preset';
        state.soundPresetId = engineName + '::' + runtimePreset.name;
        return {
          id: state.soundPresetId,
          family: engineName,
          preset: runtimePreset,
          label: engineName + ' / ' + (runtimePreset.category || 'Preset') + ' / ' + runtimePreset.name,
          runtime: true
        };
      }
    }
    var options = getSoundPresetOptions();
    var fallback = null;
    for (var i = 0; i < options.length; i++) {
      if (!fallback && options[i].family === 'subtractive') fallback = options[i];
      if (options[i].id === state.soundPresetId) return options[i];
    }
    if (fallback) {
      state.soundPresetId = fallback.id;
      return fallback;
    }
    return null;
  }

  function getSsliHost() {
    if (window.SynthLab && window.SynthLab.audio && window.SynthLab.presets) {
      return window;
    }
    var frame = document.getElementById('ssliEngineFrame');
    try {
      if (frame && frame.contentWindow && frame.contentWindow.SynthLab && frame.contentWindow.SynthLab.audio && frame.contentWindow.SynthLab.presets) {
        return frame.contentWindow;
      }
    } catch (err) {
      return null;
    }
    return null;
  }

  function getSsliEngineDisplayName(engineId, SL) {
    var map = {
      'additive': 'Additive',
      'Additive': 'Additive',
      'bytebeat': 'Bytebeat',
      'Bytebeat': 'Bytebeat',
      'fm': 'FM',
      'FM': 'FM',
      'formant': 'Formant',
      'Formant': 'Formant',
      'granular': 'Granular',
      'Granular': 'Granular',
      'modal': 'Modal',
      'Modal': 'Modal',
      'phasedist': 'PhaseDist',
      'PhaseDist': 'PhaseDist',
      'physical': 'Physical',
      'Physical': 'Physical',
      'reed': 'Reed',
      'Reed': 'Reed',
      'subtractive': 'Subtractive',
      'Subtractive': 'Subtractive',
      'vector': 'Vector',
      'Vector': 'Vector',
      'vocoder': 'Vocoder',
      'Vocoder': 'Vocoder',
      'Wavetable': 'Wavetable',
      'wavetable-synth': 'Wavetable'
    };
    var mapped = map[engineId] || engineId;
    if (SL && SL.presets && SL.presets.getEngines) {
      var engines = SL.presets.getEngines() || [];
      for (var i = 0; i < engines.length; i++) {
        if (String(engines[i]).toLowerCase() === String(mapped).toLowerCase()) return engines[i];
      }
    }
    return mapped;
  }

  function fallbackSsliEngineType(engineId) {
    var map = {
      'wavetable-synth': 'wavetable',
      'Wavetable': 'wavetable',
      'vocoder': 'vocoderSynth',
      'Vocoder': 'vocoderSynth',
      'phasedist': 'phasedist',
      'PhaseDist': 'phasedist',
      'bytebeat': 'bytebeat',
      'Bytebeat': 'bytebeat',
      'FM': 'fm',
      'Physical': 'physical',
      'Additive': 'additive',
      'Granular': 'granular',
      'Subtractive': 'subtractive',
      'Formant': 'formant',
      'Modal': 'modal',
      'Vector': 'vector',
      'Reed': 'reed'
    };
    return map[engineId] || engineId;
  }

  function toSsliEngineType(engineId, SL) {
    if (SL && SL.presets && SL.presets.engineNameToType) {
      return SL.presets.engineNameToType(getSsliEngineDisplayName(engineId, SL));
    }
    return fallbackSsliEngineType(engineId);
  }

  function clonePreset(preset) {
    return JSON.parse(JSON.stringify(preset));
  }

  function currentSsliPresetKey() {
    return [state.soundEngine, state.soundCategory, state.soundPresetId].join('|');
  }

  function invalidateSsliPresetCache() {
    lastAppliedSsliPresetKey = '';
  }

  function normalizeSsliPresetPayload(payload, SL) {
    if (!payload || !payload.settings || !payload.settings.filter) return payload;
    var filter = payload.settings.filter;
    if (typeof filter.freq !== 'number') return payload;
    if (filter.freq < 0) filter.freq = 0;
    if (filter.freq > 1000) {
      var hz = Math.min(20000, filter.freq);
      filter.freq = SL && SL.audio && SL.audio.freqToSlider ? SL.audio.freqToSlider(hz) : 1000;
      logEvent('audio', 'SSLI preset filter normalized ' + (payload.name || state.soundPresetId) + ' cutoff=' + Math.round(hz) + 'Hz');
    }
    return payload;
  }

  function findSsliRuntimePreset(SL, selected, engineName) {
    if (selected && selected.runtime) return selected.preset;
    if (!SL || !SL.presets || !SL.presets.getPresetsForEngineCategory) return null;
    var category = selected.preset.category || state.soundCategory || 'Preset';
    var lists = [];
    try {
      lists.push(SL.presets.getPresetsForEngineCategory(engineName, category) || []);
    } catch (err) {
      logEvent('audio', 'SSLI runtime preset lookup warning ' + engineName + ' / ' + category + ': ' + (err && err.message ? err.message : err));
    }
    if (SL.presets.getCategoriesForEngine) {
      try {
        var categories = SL.presets.getCategoriesForEngine(engineName) || [];
        for (var i = 0; i < categories.length; i++) {
          if (categories[i] === category) continue;
          lists.push(SL.presets.getPresetsForEngineCategory(engineName, categories[i]) || []);
        }
      } catch (err2) {
        logEvent('audio', 'SSLI runtime category lookup warning ' + engineName + ': ' + (err2 && err2.message ? err2.message : err2));
      }
    }
    for (var listIndex = 0; listIndex < lists.length; listIndex++) {
      for (var presetIndex = 0; presetIndex < lists[listIndex].length; presetIndex++) {
        if (lists[listIndex][presetIndex] && lists[listIndex][presetIndex].name === selected.preset.name) {
          return lists[listIndex][presetIndex];
        }
      }
    }
    return null;
  }

  function getSsliPresetPayload(SL) {
    var selected = getCurrentSoundPreset();
    if (!selected || !selected.preset) return null;
    var engineName = getSsliEngineDisplayName(selected.family, SL);
    var runtimePreset = findSsliRuntimePreset(SL, selected, engineName);
    var payload = clonePreset(runtimePreset || selected.preset);
    payload.engine = toSsliEngineType(engineName, SL);
    normalizeSsliPresetPayload(payload, SL);
    return payload;
  }

  function applySelectedSsliPreset() {
    var host = getSsliHost();
    if (!host) return false;
    var SL = host.SynthLab;
    var presetKey = currentSsliPresetKey();
    if (lastAppliedSsliPresetKey === presetKey) return true;
    var preset = getSsliPresetPayload(SL);
    if (!preset || !SL.presets || !SL.presets.apply || !SL.audio) return false;
    if (SL.audio.stopAllSustained) SL.audio.stopAllSustained();
    if (SL.audio.getCtx) {
      var ctx = SL.audio.getCtx();
      if (ctx && ctx.state === 'suspended' && ctx.resume) ctx.resume();
    }
    var inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    SL.presets.apply(preset, inst);
    if (SL.state && SL.state.notify) SL.state.notify('preset');
    lastAppliedSsliPresetKey = presetKey;
    state.audioStatus = 'Audio: SSLI ' + (preset.name || state.soundPresetId) + '.';
    logEvent('audio', 'SSLI preset applied engine=' + preset.engine + ' preset=' + state.soundPresetId);
    return true;
  }

  function getSsliInstrument(SL) {
    if (!SL || !SL.audio || !SL.audio.getInstruments) return null;
    var instruments = SL.audio.getInstruments();
    var inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    return instruments && instruments[inst] ? { id: inst, instrument: instruments[inst] } : null;
  }

  function getCurrentSsliInstrumentType(SL) {
    var current = getSsliInstrument(SL);
    return current && current.instrument ? current.instrument.type || '' : '';
  }

  function ensureSsliPracticeVolume(SL, inst) {
    if (!SL || !SL.audio || !SL.audio.getInstruments) return;
    var instruments = SL.audio.getInstruments() || [];
    var instrument = instruments[inst] || {};
    var settings = instrument.settings || {};
    var currentVolume = typeof settings.volume === 'number' ? settings.volume : null;
    var targetVolume = 100;
    if (SL.audio.setInstrumentVolume && (currentVolume === null || currentVolume < targetVolume)) {
      SL.audio.setInstrumentVolume(inst, targetVolume);
      logEvent('audio', 'SSLI instrument inst=' + inst + ' type=' + (instrument.type || 'unknown') + ' volume=' + (currentVolume === null ? 'unset' : currentVolume) + '->' + targetVolume);
    } else {
      logEvent('audio', 'SSLI instrument inst=' + inst + ' type=' + (instrument.type || 'unknown') + ' volume=' + (currentVolume === null ? 'unset' : currentVolume));
    }
  }

  function ensureSsliPracticeOutputBoost(SL) {
    if (!SL || !SL.audio || !SL.audio.getCtx || !SL.audio.getFinalDestination) return false;
    if (SL.__exquisPracticeOutputBoost && SL.audio.getFinalDestination.__exquisBoosted) return true;
    var ctx = SL.audio.getCtx();
    if (!ctx || !ctx.createGain) return false;
    var originalGetFinalDestination = SL.audio.getFinalDestination;
    var originalDestination = originalGetFinalDestination.call(SL.audio);
    if (!originalDestination) return false;
    var boost = ctx.createGain();
    boost.gain.value = SSLI_PRACTICE_OUTPUT_GAIN;
    boost.connect(originalDestination);
    SL.__exquisPracticeOutputBoost = boost;
    SL.__exquisOriginalGetFinalDestination = originalGetFinalDestination;
    SL.audio.getFinalDestination = function() {
      return SL.__exquisPracticeOutputBoost || originalGetFinalDestination.call(SL.audio);
    };
    SL.audio.getFinalDestination.__exquisBoosted = true;
    logEvent('audio', 'SSLI output boost gain=' + SSLI_PRACTICE_OUTPUT_GAIN);
    return true;
  }

  function ensureSsliAudioReady(SL) {
    if (!SL || !SL.audio) return;
    if (SL.audio.getCtx) SL.audio.getCtx();
    if (SL.audio.initEffectChain) SL.audio.initEffectChain();
    if (!SL.__exquisEnginesInitialized) {
      [
        'fm', 'physical', 'additive', 'granular', 'vocoderSynth',
        'wavefolder', 'formant', 'modal', 'ringmod', 'chord',
        'superwave', 'wavetableSynth', 'phasedist', 'chip',
        'bytebeat', 'vector', 'drumsyn', 'pulsar', 'bodyResonance', 'reed'
      ].forEach(function(engineName) {
        var engine = SL[engineName];
        if (!engine || !engine.init) return;
        try {
          engine.init();
        } catch (err) {
          logEvent('audio', 'SSLI engine init warning ' + engineName + ': ' + (err && err.message ? err.message : err));
        }
      });
      SL.__exquisEnginesInitialized = true;
    }
  }

  function applySelectedSsliFilter() {
    var host = getSsliHost();
    if (!host) return false;
    var SL = host.SynthLab;
    ensureSsliAudioReady(SL);
    var current = getSsliInstrument(SL);
    if (!current || !current.instrument.settings) return false;
    var filter = current.instrument.settings.filter || {};
    filter.enabled = true;
    filter.type = state.filterType || filter.type || 'lowpass';
    filter.freq = SL.audio.freqToSlider ? SL.audio.freqToSlider(state.filterCutoff) : state.filterCutoff;
    filter.q = SL.audio.qToSlider ? SL.audio.qToSlider(state.filterResonance) : state.filterResonance;
    filter.keyTrack = typeof filter.keyTrack === 'number' ? filter.keyTrack : 0;
    filter.model = filter.model || 'butterworth';
    filter.slope = filter.slope || 24;
    current.instrument.settings.filter = filter;
    if (SL.audio.loadInstrumentSettings) SL.audio.loadInstrumentSettings(current.id);
    if (SL.audio.refreshFilter) SL.audio.refreshFilter();
    logEvent('audio', 'SSLI filter type=' + filter.type + ' cutoff=' + Math.round(state.filterCutoff) + 'Hz resonance=' + state.filterResonance);
    return true;
  }

  function applySelectedSsliFxChain() {
    var host = getSsliHost();
    if (!host) return false;
    var SL = host.SynthLab;
    if (!SL || !SL.audio || !SL.audio.getInstrumentChain) return false;
    ensureSsliAudioReady(SL);
    var current = getSsliInstrument(SL);
    var inst = current ? current.id : (SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0);
    var chain = SL.audio.getInstrumentChain(inst);
    if (!chain) return false;
    var preset = getCurrentFxPreset();
    var effects = preset.effects || [];
    var order = [];
    if (chain.getAvailableEffects) {
      chain.getAvailableEffects().forEach(function(name) {
        var existing = chain.getEffect ? chain.getEffect(name) : null;
        if (existing && existing.setEnabled) existing.setEnabled(false);
      });
    }
    for (var i = 0; i < effects.length; i++) {
      var fx = effects[i];
      order.push(fx.name);
      if (chain.addToChain) chain.addToChain(fx.name);
      var effect = chain.getEffect ? chain.getEffect(fx.name) : null;
      if (!effect) continue;
      if (effect.setEnabled) effect.setEnabled(true);
      var params = fx.params || {};
      Object.keys(params).forEach(function(paramName) {
        if (effect.setParam) effect.setParam(paramName, params[paramName]);
      });
    }
    if (chain.setOrder) chain.setOrder(order);
    if (chain.setMasterMix) chain.setMasterMix(effects.length ? 100 : 0);
    if (current && current.instrument.settings) {
      current.instrument.settings.effects = {
        chainOrder: order.slice(),
        masterMix: effects.length ? 100 : 0,
        enabled: {},
        params: {}
      };
      effects.forEach(function(fx) {
        current.instrument.settings.effects.enabled[fx.name] = true;
        current.instrument.settings.effects.params[fx.name] = Object.assign({}, fx.params || {});
      });
    }
    logEvent('audio', 'SSLI FX chain ' + (preset.label || preset.id || 'Dry') + ' effects=' + order.join(','));
    return true;
  }

  function playWithSsli(midi, duration, velocity) {
    var host = getSsliHost();
    if (!host) return false;
    var SL = host.SynthLab;
    if (!SL || !SL.audio || !SL.audio.playNoteOnInstrument) return false;
    ensureSsliAudioReady(SL);
    applySelectedSsliPreset();
    if (state.filterDirty) applySelectedSsliFilter();
    if (state.fxDirty) applySelectedSsliFxChain();
    var instrumentType = getCurrentSsliInstrumentType(SL);
    var expressionMode = 'max';
    if (instrumentType !== 'physical') {
      setSsliMidiExpression(127);
    } else {
      expressionMode = 'native';
    }
    var inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    SL.audio.playNoteOnInstrument(midi, duration || 0.55, inst, Math.max(127, velocity || 100));
    state.audioStatus = 'Audio: SSLI playing ' + noteLabelFromMidi(midi) + '.';
    logEvent('audio', 'SSLI play ' + noteLabelFromMidi(midi) + ' velocity=127 expression=' + expressionMode + ' preset=' + state.soundPresetId + ' inst=' + inst);
    startAudioScope();
    window.setTimeout(clearSsliMidiExpressionIfIdle, Math.max(220, (duration || 0.55) * 1000));
    render();
    return true;
  }

  function pressureToSsliExpression(pressure) {
    var level = Math.max(0, Math.min(1, (pressure || 0) / 127));
    return {
      cutoffHz: 900 + level * 9100,
      gain: Math.max(0.75, Math.min(2, 0.75 + level * 1.25))
    };
  }

  function playableSsliMidiVelocity(velocity) {
    return 127;
  }

  function forgetHeldVoiceKey(key) {
    var voice = midiVoices[key];
    delete state.heldNotes[key];
    if (voice) {
      Object.keys(state.channelNotes).forEach(function(channel) {
        if (state.channelNotes[channel] === voice.midi && key === voiceKey(channel, voice.midi)) {
          delete state.channelNotes[channel];
        }
      });
    }
  }

  function pruneMidiVoiceBudget(nextKey) {
    var activeKeys = Object.keys(midiVoices).filter(function(key) { return key !== nextKey; });
    activeKeys.sort(function(a, b) {
      return (midiVoices[a].startedAt || 0) - (midiVoices[b].startedAt || 0);
    });
    while (activeKeys.length >= MIDI_VOICE_BUDGET) {
      var staleKey = activeKeys.shift();
      var staleVoice = midiVoices[staleKey];
      forgetHeldVoiceKey(staleKey);
      releaseMidiVoice(staleKey, true);
      if (staleVoice) {
        logEvent('audio', 'pruned stale MIDI voice ' + noteLabelFromMidi(staleVoice.midi));
      }
    }
  }

  function setSsliMidiExpression(pressure) {
    var host = getSsliHost();
    if (!host || !host.SynthLab || !host.SynthLab.audio || !host.SynthLab.audio.setExpression) return false;
    var SL = host.SynthLab;
    ensureSsliAudioReady(SL);
    var expression = pressureToSsliExpression(pressure);
    SL.audio.setExpression(expression.cutoffHz, expression.gain);
    logEvent('audio', 'SSLI expression pressure=' + pressure + ' cutoff=' + Math.round(expression.cutoffHz) + 'Hz gain=' + expression.gain.toFixed(2));
    return true;
  }

  function strongestHeldMidiPressure() {
    var strongest = 0;
    Object.keys(state.heldNotes).forEach(function(key) {
      var held = state.heldNotes[key];
      if (!held) return;
      var pressure = typeof held.pressure === 'number' ? held.pressure : (held.velocity || 0);
      strongest = Math.max(strongest, pressure);
    });
    return strongest;
  }

  function updateSsliExpressionFromHeldNotes() {
    var strongest = strongestHeldMidiPressure();
    if (strongest > 0) {
      setSsliMidiExpression(strongest);
      return true;
    }
    clearSsliMidiExpression();
    return false;
  }

  function clearSsliMidiExpression() {
    var host = getSsliHost();
    if (host && host.SynthLab && host.SynthLab.audio && host.SynthLab.audio.clearExpression) {
      host.SynthLab.audio.clearExpression();
      logEvent('audio', 'SSLI expression cleared');
      return true;
    }
    return false;
  }

  function clearSsliMidiExpressionIfIdle() {
    var hasHeldSsliVoice = Object.keys(midiVoices).some(function(key) {
      return midiVoices[key] && midiVoices[key].ssli;
    });
    if (hasHeldSsliVoice) return;
    clearSsliMidiExpression();
  }

  function startSustainedWithSsli(midi, velocity) {
    var host = getSsliHost();
    if (!host) return false;
    var SL = host.SynthLab;
    if (!SL || !SL.audio || !SL.audio.startSustainedNote) return false;
    ensureSsliAudioReady(SL);
    applySelectedSsliPreset();
    if (state.filterDirty) applySelectedSsliFilter();
    if (state.fxDirty) applySelectedSsliFxChain();
    var inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    ensureSsliPracticeVolume(SL, inst);
    ensureSsliPracticeOutputBoost(SL);
    var playableVelocity = playableSsliMidiVelocity(velocity);
    SL.audio.startSustainedNote(midi, playableVelocity);
    setSsliMidiExpression(Math.max(1, velocity || 1));
    state.audioStatus = 'Audio: SSLI held ' + noteLabelFromMidi(midi) + '.';
    logEvent('audio', 'SSLI MIDI sustain start ' + noteLabelFromMidi(midi) + ' velocity=' + playableVelocity + ' pressure=' + Math.max(1, velocity || 1) + ' preset=' + state.soundPresetId);
    startAudioScope();
    render();
    return true;
  }

  function stopSustainedWithSsli(midi) {
    var host = getSsliHost();
    if (!host || !host.SynthLab || !host.SynthLab.audio || !host.SynthLab.audio.stopSustainedNote) return false;
    host.SynthLab.audio.stopSustainedNote(midi);
    logEvent('audio', 'SSLI MIDI sustain stop ' + noteLabelFromMidi(midi));
    return true;
  }

  function getFxPresetOptions() {
    var options = [{ id: 'dry', label: 'Dry', preset: { id: 'dry', label: 'Dry', effects: [] } }];
    var library = SSLI_FX_PRESETS.library || {};
    Object.keys(library).forEach(function(category) {
      for (var i = 0; i < library[category].length; i++) {
        var preset = library[category][i];
        options.push({
          id: preset.id,
          label: category + ' / ' + preset.label,
          preset: preset
        });
      }
    });
    return options;
  }

  function getFxCategories() {
    return Object.keys(SSLI_FX_PRESETS.library || {}).sort();
  }

  function getFxPresetsFor(category) {
    if (category === 'Clean / Natural') {
      return [{ id: 'dry', label: 'Dry', effects: [] }].concat((SSLI_FX_PRESETS.library || {})[category] || []);
    }
    return ((SSLI_FX_PRESETS.library || {})[category] || []).slice();
  }

  function syncFxSelectorsFromPreset() {
    if (state.fxPresetId === 'dry') {
      state.fxCategory = 'Clean / Natural';
      return;
    }
    var library = SSLI_FX_PRESETS.library || {};
    Object.keys(library).forEach(function(category) {
      for (var i = 0; i < library[category].length; i++) {
        if (library[category][i].id === state.fxPresetId) state.fxCategory = category;
      }
    });
  }

  function getCurrentFxPreset() {
    var options = getFxPresetOptions();
    for (var i = 0; i < options.length; i++) {
      if (options[i].id === state.fxPresetId) return options[i].preset;
    }
    state.fxPresetId = 'dry';
    return options[0].preset;
  }

  function midiToFreq(midi) {
    return 440 * Math.pow(2, (midi - 69) / 12);
  }

  function ensureAudio() {
    if (!audioCtx) {
      var AudioContextCtor = window.AudioContext || window.webkitAudioContext;
      if (AudioContextCtor) {
        audioCtx = new AudioContextCtor();
        audioAnalyser = audioCtx.createAnalyser ? audioCtx.createAnalyser() : null;
        if (audioAnalyser) {
          audioAnalyser.fftSize = 1024;
          audioScopeData = new Uint8Array(audioAnalyser.fftSize);
        }
        ensureFxBus(audioCtx);
        logEvent('audio', 'created AudioContext, state=' + audioCtx.state);
      } else {
        logEvent('audio', 'WebAudio unavailable: no AudioContext constructor');
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      logEvent('audio', 'resume requested from suspended state');
      var resumeResult = audioCtx.resume();
      if (resumeResult && resumeResult.then) {
        resumeResult.then(function() {
          state.audioStatus = 'Audio: ' + audioCtx.state + '.';
          logEvent('audio', 'resume resolved, state=' + audioCtx.state);
          render();
        }).catch(function(err) {
          state.audioStatus = 'Audio: resume failed.';
          logEvent('audio', 'resume failed: ' + (err && err.message ? err.message : err));
          render();
        });
      }
    }
    state.audioStatus = audioCtx ? 'Audio: ' + audioCtx.state + '.' : 'Audio: WebAudio unavailable.';
    return audioCtx;
  }

  function drawAudioScope() {
    if (!els.audioScope) return;
    var canvas = els.audioScope;
    var ctx2d = canvas.getContext && canvas.getContext('2d');
    if (!ctx2d) return;
    var width = canvas.width;
    var height = canvas.height;
    ctx2d.clearRect(0, 0, width, height);
    ctx2d.fillStyle = '#0d1114';
    ctx2d.fillRect(0, 0, width, height);
    ctx2d.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx2d.beginPath();
    ctx2d.moveTo(0, height / 2);
    ctx2d.lineTo(width, height / 2);
    ctx2d.stroke();

    if (!audioAnalyser || !audioScopeData) {
      if (els.scopeReadout) els.scopeReadout.textContent = 'Output: no analyser / peak 0%';
      return;
    }

    audioAnalyser.getByteTimeDomainData(audioScopeData);
    var peak = 0;
    var displayData = audioScopeData;
    var nowMs = Date.now();
    for (var p = 0; p < audioScopeData.length; p++) {
      peak = Math.max(peak, Math.abs((audioScopeData[p] - 128) / 128));
    }
    if (peak > 0.03) {
      heldScopeData = new Uint8Array(audioScopeData);
      heldScopePeak = peak;
      heldScopeUntil = nowMs + 4500;
    } else if (heldScopeData && nowMs < heldScopeUntil) {
      displayData = heldScopeData;
      peak = heldScopePeak;
    }
    ctx2d.strokeStyle = '#62d2a2';
    ctx2d.lineWidth = 2;
    ctx2d.beginPath();
    for (var i = 0; i < displayData.length; i++) {
      var normalized = (displayData[i] - 128) / 128;
      var x = (i / (displayData.length - 1)) * width;
      var y = (0.5 - normalized * 0.42) * height;
      if (i === 0) ctx2d.moveTo(x, y);
      else ctx2d.lineTo(x, y);
    }
    ctx2d.stroke();
    ctx2d.fillStyle = 'rgba(246,198,91,0.85)';
    ctx2d.fillRect(0, height - 8, width * Math.min(1, peak), 8);
    if (els.scopeReadout) {
      els.scopeReadout.textContent = 'Output: ' + (audioCtx ? audioCtx.state : 'off') + ' / peak ' + Math.round(peak * 100) + '%';
    }
  }

  function startAudioScope() {
    drawAudioScope();
    if (audioScopeTimer) return;
    var startedAt = Date.now();
    audioScopeTimer = window.setInterval(function() {
      drawAudioScope();
      if (Date.now() - startedAt > 5000) {
        window.clearInterval(audioScopeTimer);
        audioScopeTimer = null;
        drawAudioScope();
      }
    }, 50);
  }

  function disconnectNode(node) {
    try {
      node.disconnect();
    } catch (err) {
      // Some nodes may not have active connections yet.
    }
  }

  function createDriveCurve(amount) {
    var samples = 1024;
    var curve = new Float32Array(samples);
    var drive = 1 + (amount || 0) / 12;
    for (var i = 0; i < samples; i++) {
      var x = (i * 2) / samples - 1;
      curve[i] = Math.tanh(x * drive);
    }
    return curve;
  }

  function getRenderablePresetSettings() {
    var selected = getCurrentSoundPreset();
    var settings = selected && selected.preset ? selected.preset.settings || {} : {};
    if (!settings.osc) {
      return {
        osc: [
          { wave: state.tone === 'round_sine' ? 'sine' : 'triangle', oct: 0, detune: 0, level: 80 },
          { wave: state.tone === 'muted_pluck' ? 'square' : 'sine', oct: 1, detune: 0, level: 22 }
        ],
        adsr: { a: 8, d: 180, s: 45, r: 180 },
        filter: { enabled: true, type: state.filterType, freq: state.filterCutoff, q: state.filterResonance, keyTrack: 30 }
      };
    }
    return settings;
  }

  function clampAudioWave(wave) {
    return ['sine', 'square', 'sawtooth', 'triangle'].indexOf(wave) >= 0 ? wave : 'sine';
  }

  function createPresetOscillators(ctx, midi, baseFreq, output, velocityLevel) {
    var settings = getRenderablePresetSettings();
    var oscSettings = settings.osc || [];
    var nodes = [];
    var totalLevel = 0;
    for (var i = 0; i < oscSettings.length; i++) {
      totalLevel += Math.max(0, oscSettings[i].level || 0);
    }
    if (totalLevel <= 0) totalLevel = 100;
    for (var o = 0; o < oscSettings.length; o++) {
      var oscSetting = oscSettings[o];
      var level = Math.max(0, oscSetting.level || 0);
      if (level <= 0) continue;
      var osc = ctx.createOscillator();
      var gain = ctx.createGain();
      osc.type = clampAudioWave(oscSetting.wave || 'sine');
      osc.frequency.value = baseFreq * Math.pow(2, oscSetting.oct || 0);
      if (osc.detune) osc.detune.value = oscSetting.detune || 0;
      gain.gain.value = (level / totalLevel) * (0.85 + velocityLevel * 0.25);
      osc.connect(gain);
      gain.connect(output);
      osc.start(ctx.currentTime);
      nodes.push({ osc: osc, gain: gain });
    }
    return nodes;
  }

  function applyPresetFilterSettings(filter, midi, baseFreq) {
    var settings = getRenderablePresetSettings();
    var presetFilter = settings.filter || {};
    filter.type = state.filterType || presetFilter.type || 'lowpass';
    var baseCutoff = presetFilter.enabled === false ? 18000 : (presetFilter.freq || state.filterCutoff || 2200);
    var keyTrack = (presetFilter.keyTrack || 0) / 100;
    var tracked = baseCutoff * Math.pow(2, Math.log2(baseFreq / 261.63) * keyTrack);
    filter.frequency.value = Math.max(80, Math.min(18000, tracked));
    filter.Q.value = Math.max(0.2, Math.min(24, presetFilter.q ? presetFilter.q / 5 : state.filterResonance));
  }

  function createSimpleEffect(ctx, effect) {
    var name = effect.name;
    var params = effect.params || {};
    var input = ctx.createGain();
    var output = ctx.createGain();
    var wet = ctx.createGain();
    var dry = ctx.createGain();
    var mix = Math.max(0, Math.min(1, (params.mix == null ? 35 : params.mix) / 100));
    dry.gain.value = 1 - mix;
    wet.gain.value = mix;
    input.connect(dry);
    dry.connect(output);
    wet.connect(output);

    if (name === 'filter') {
      var filter = ctx.createBiquadFilter();
      filter.type = params.type || state.filterType || 'lowpass';
      filter.frequency.value = params.frequency || state.filterCutoff;
      filter.Q.value = params.resonance || state.filterResonance;
      input.connect(filter);
      filter.connect(wet);
    } else if (name === 'distortion' || name === 'softClip' || name === 'tape') {
      var shaper = ctx.createWaveShaper();
      shaper.curve = createDriveCurve(params.drive || params.threshold || 25);
      shaper.oversample = '2x';
      input.connect(shaper);
      shaper.connect(wet);
    } else if (name === 'compressor' && ctx.createDynamicsCompressor) {
      var comp = ctx.createDynamicsCompressor();
      comp.threshold.value = params.threshold || -18;
      comp.ratio.value = params.ratio || 4;
      input.connect(comp);
      comp.connect(wet);
    } else if (name === 'chorus' || name === 'dimension' || name === 'flanger') {
      var delay = ctx.createDelay ? ctx.createDelay(0.08) : null;
      if (!delay) return { input: input, output: output };
      delay.delayTime.value = name === 'flanger' ? 0.006 : 0.018 + ((params.depth || 25) / 10000);
      input.connect(delay);
      delay.connect(wet);
    } else if (name === 'delay' || name === 'reverb' || name === 'gatedReverb') {
      var d = ctx.createDelay ? ctx.createDelay(2) : null;
      if (!d) return { input: input, output: output };
      var fb = ctx.createGain();
      d.delayTime.value = Math.max(0.03, Math.min(1.5, (params.time || (name === 'reverb' ? 90 : 320)) / 1000));
      fb.gain.value = Math.max(0, Math.min(0.82, (params.feedback || params.decay || 18) / 100));
      input.connect(d);
      d.connect(fb);
      fb.connect(d);
      d.connect(wet);
    } else if (name === 'eq') {
      var low = ctx.createBiquadFilter();
      var high = ctx.createBiquadFilter();
      low.type = 'lowshelf';
      high.type = 'highshelf';
      low.frequency.value = 240;
      high.frequency.value = 2800;
      low.gain.value = params.lowGain || 0;
      high.gain.value = params.highGain || 0;
      input.connect(low);
      low.connect(high);
      high.connect(wet);
    } else {
      input.connect(wet);
    }

    return { input: input, output: output };
  }

  function ensureFxBus(ctx) {
    if (!ctx) return null;
    if (!fxInput) {
      fxInput = ctx.createGain();
      fxOutput = ctx.createGain();
      if (fxOutput.gain && fxOutput.gain.setValueAtTime) {
        fxOutput.gain.setValueAtTime(LOCAL_MASTER_GAIN, ctx.currentTime || 0);
      } else if (fxOutput.gain) {
        fxOutput.gain.value = LOCAL_MASTER_GAIN;
      }
    }
    rebuildFxBus(ctx);
    return fxInput;
  }

  function rebuildFxBus(ctx) {
    if (!fxInput || !fxOutput) return;
    disconnectNode(fxInput);
    for (var i = 0; i < fxNodes.length; i++) {
      disconnectNode(fxNodes[i].input);
      disconnectNode(fxNodes[i].output);
    }
    disconnectNode(fxOutput);
    fxNodes = [];

    var preset = getCurrentFxPreset();
    var effects = preset.effects || [];
    var previous = fxInput;
    if (effects.length === 0) {
      previous.connect(fxOutput);
    } else {
      for (var e = 0; e < effects.length; e++) {
        var fx = createSimpleEffect(ctx, effects[e]);
        previous.connect(fx.input);
        previous = fx.output;
        fxNodes.push(fx);
      }
      previous.connect(fxOutput);
    }
    fxOutput.connect(audioAnalyser || ctx.destination);
    if (audioAnalyser) audioAnalyser.connect(ctx.destination);
    logEvent('audio', 'FX chain ' + (preset.label || preset.id || 'Dry') + ' effects=' + effects.map(function(effect) { return effect.name; }).join(','));
  }

  function playNote(midi, duration, localOnly) {
    if (!localOnly && playWithSsli(midi, duration || 0.55, 100)) return;
    var ctx = ensureAudio();
    if (!ctx) {
      logEvent('audio', 'playNote aborted: no audio context');
      render();
      return;
    }
    var now = ctx.currentTime;
    var dur = duration || 0.55;
    var out = ctx.createGain();
    var filter = ctx.createBiquadFilter();
    var freq = midiToFreq(midi);
    var settings = getRenderablePresetSettings();
    var adsr = settings.adsr || { a: 8 };

    var peakGain = localOnly ? 0.98 : 0.72;
    var sustainGain = localOnly ? 0.52 : 0.34;
    out.gain.setValueAtTime(0.0001, now);
    out.gain.exponentialRampToValueAtTime(peakGain, now + Math.max(0.004, (adsr.a || 8) / 1000));
    out.gain.exponentialRampToValueAtTime(sustainGain, now + 0.16);
    out.gain.exponentialRampToValueAtTime(0.0001, now + dur);

    var oscNodes = createPresetOscillators(ctx, midi, freq, filter, 0.75);
    applyPresetFilterSettings(filter, midi, freq);
    filter.connect(out);
    connectAudioOut(out, ctx);

    for (var oi = 0; oi < oscNodes.length; oi++) {
      oscNodes[oi].osc.stop(now + dur + 0.02);
    }
    state.audioStatus = 'Audio: playing ' + noteLabelFromMidi(midi) + '.';
    logEvent('audio', (localOnly ? 'local test tone ' : 'playing ') + noteLabelFromMidi(midi) + ' freq=' + Math.round(freq * 10) / 10 + 'Hz preset=' + state.soundPresetId + ' fx=' + state.fxPresetId + ' ctx=' + ctx.state);
    startAudioScope();
    window.setTimeout(function() {
      state.audioStatus = audioCtx ? 'Audio: ' + audioCtx.state + '.' : 'Audio: unavailable.';
      render();
    }, Math.max(220, dur * 1000));
    render();
  }

  function connectAudioOut(node, ctx) {
    var bus = ensureFxBus(ctx);
    node.connect(bus || audioAnalyser || ctx.destination);
    if (!bus && audioAnalyser) audioAnalyser.connect(ctx.destination);
  }

  function startMidiVoice(key, midi, velocity) {
    releaseMidiVoice(key, true);
    pruneMidiVoiceBudget(key);
    if (startSustainedWithSsli(midi, Math.max(1, velocity))) {
      midiVoices[key] = { midi: midi, ssli: true, startedAt: Date.now() };
      return;
    }
    var ctx = ensureAudio();
    if (!ctx) {
      logEvent('audio', 'MIDI voice aborted: no audio context for ' + noteLabelFromMidi(midi));
      return;
    }
    var now = ctx.currentTime;
    var freq = midiToFreq(midi);
    var out = ctx.createGain();
    var filter = ctx.createBiquadFilter();
    var playableVelocity = playableSsliMidiVelocity(velocity);
    var level = Math.max(0.06, Math.min(1, playableVelocity / 127));
    var settings = getRenderablePresetSettings();
    var adsr = settings.adsr || { a: 8, s: 45 };

    out.gain.setValueAtTime(0.0001, now);
    out.gain.exponentialRampToValueAtTime(0.08 + level * 0.28, now + Math.max(0.004, (adsr.a || 8) / 1000));
    var oscNodes = createPresetOscillators(ctx, midi, freq, filter, level);
    applyPresetFilterSettings(filter, midi, freq);
    filter.connect(out);
    connectAudioOut(out, ctx);

    midiVoices[key] = {
      midi: midi,
      gain: out,
      filter: filter,
      oscillators: oscNodes,
      releaseMs: adsr.r || 180,
      startedAt: Date.now()
    };
    state.audioStatus = 'Audio: MIDI voice ' + noteLabelFromMidi(midi) + '.';
    logEvent('audio', 'MIDI voice start ' + noteLabelFromMidi(midi) + ' velocity=' + playableVelocity + ' pressure=' + Math.max(1, velocity || 1) + ' preset=' + state.soundPresetId + ' ctx=' + ctx.state);
    startAudioScope();
  }

  function updateMidiVoicePressure(key, pressure) {
    var voice = midiVoices[key];
    if (!voice) return;
    if (voice.ssli) {
      updateSsliExpressionFromHeldNotes();
      return;
    }
    if (!audioCtx) return;
    var now = audioCtx.currentTime;
    var level = Math.max(0.03, Math.min(1, pressure / 127));
    voice.gain.gain.cancelScheduledValues && voice.gain.gain.cancelScheduledValues(now);
    voice.gain.gain.setTargetAtTime ? voice.gain.gain.setTargetAtTime(0.04 + level * 0.32, now, 0.025) : voice.gain.gain.setValueAtTime(0.04 + level * 0.32, now);
    if (voice.filter && voice.filter.frequency) {
      voice.filter.frequency.setTargetAtTime ? voice.filter.frequency.setTargetAtTime(1500 + level * 3200, now, 0.04) : voice.filter.frequency.value = 1500 + level * 3200;
    }
  }

  function releaseMidiVoice(key, immediate) {
    var voice = midiVoices[key];
    if (voice && voice.ssli) {
      stopSustainedWithSsli(voice.midi);
      delete midiVoices[key];
      clearSsliMidiExpressionIfIdle();
      return;
    }
    if (!voice || !audioCtx) return;
    var now = audioCtx.currentTime;
    var stopAt = immediate ? now + 0.01 : now + Math.max(0.04, Math.min(1.4, (voice.releaseMs || 180) / 1000));
    try {
      if (voice.gain && voice.gain.gain) {
        voice.gain.gain.cancelScheduledValues && voice.gain.gain.cancelScheduledValues(now);
        voice.gain.gain.setValueAtTime(Math.max(0.0001, voice.gain.gain.value || 0.0001), now);
        voice.gain.gain.exponentialRampToValueAtTime(0.0001, stopAt);
      }
      var oscillators = voice.oscillators || [];
      for (var i = 0; i < oscillators.length; i++) {
        oscillators[i].osc.stop(stopAt + 0.02);
      }
    } catch (err) {
      logEvent('audio', 'voice release warning: ' + (err && err.message ? err.message : err));
    }
    delete midiVoices[key];
  }

  function pressUiKey(cell, pressure) {
    var key = voiceKey('ui', cell.midi);
    state.heldNotes[key] = {
      midi: cell.midi,
      pc: cell.pc,
      velocity: pressure,
      pressure: pressure,
      cellId: cell.id,
      channel: 'ui'
    };
    state.activeMidiCellId = cell.id;
    state.activeMidiPc = cell.pc;
    state.rawMidiFlash = false;
    state.lastMidi = { midi: cell.midi, velocity: pressure, cellId: cell.id };
    startMidiVoice(key, cell.midi, pressure);
    logEvent('ui', 'key down ' + noteLabelFromMidi(cell.midi) + ' midi=' + cell.midi);
    render();
  }

  function releaseUiKey(cell) {
    var key = voiceKey('ui', cell.midi);
    if (!state.heldNotes[key]) return;
    delete state.heldNotes[key];
    releaseMidiVoice(key, false);
    logEvent('ui', 'key up ' + noteLabelFromMidi(cell.midi) + ' midi=' + cell.midi);
    render();
  }

  function releaseAllUiKeys() {
    var released = false;
    Object.keys(state.heldNotes).forEach(function(key) {
      if (key.indexOf('ui:') === 0) {
        releaseMidiVoice(key, false);
        delete state.heldNotes[key];
        released = true;
      }
    });
    if (released) {
      logEvent('ui', 'released all UI keys');
      render();
    }
  }

  function playCurrent() {
    if (!currentPath.length) return;
    var current = currentPath[mod(state.step, currentPath.length)];
    playNote(current.midi, 0.62);
  }

  function playTestTone() {
    playNote(60, 0.7, true);
  }

  function resetConsole() {
    logs = [];
    resetVisualMidi();
    if (els.diagnosticLog) els.diagnosticLog.textContent = 'Ready.';
    logEvent('console', 'reset');
    render();
  }

  function copyConsole() {
    var text = logs.join('\n') || 'Ready.';
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function() {
        logEvent('console', 'copied log to clipboard');
        render();
      }).catch(function(err) {
        logEvent('console', 'copy failed: ' + (err && err.message ? err.message : err));
        render();
      });
    } else {
      logEvent('console', 'copy unavailable in this browser context');
      render();
    }
  }

  function exitConsole() {
    if (els.consolePanel) {
      els.consolePanel.hidden = true;
      logEvent('console', 'hidden');
    }
  }

  function playPath() {
    var ctx = ensureAudio();
    if (!ctx || !currentPath.length) return;
    for (var i = 0; i < currentPath.length; i++) {
      (function(idx) {
        window.setTimeout(function() {
          state.step = idx;
          render();
          playNote(currentPath[idx].midi, 0.38);
        }, idx * 420);
      })(i);
    }
  }

  function getTonicName() {
    for (var i = 0; i < TONICS.length; i++) {
      if (TONICS[i].pc === state.tonicPc) return TONICS[i].name;
    }
    return 'C';
  }

  function makeGrid(scale) {
    scale = scale || 1;
    var cells = [];
    var rows = EXQUIS_NOTE_ROWS;
    var baseWidth = (state.orientation === 'horizontal' ? SURFACE_HORIZONTAL_W : SURFACE_W) * scale;
    var baseHeight = SURFACE_H * scale;
    var rotation = mod(state.rotation, 360);
    var rotatedWidth = rotation === 90 || rotation === 270 ? baseHeight : baseWidth;
    var rotatedHeight = rotation === 90 || rotation === 270 ? baseWidth : baseHeight;
    var cx = baseWidth / 2;
    var cy = baseHeight / 2;
    var rcx = rotatedWidth / 2;
    var rcy = rotatedHeight / 2;
    for (var row = 0; row < rows.length; row++) {
      var count = rows[row].length;
      var rowOffset = count === 5 ? 0.5 : 0;
      for (var col = 0; col < count; col++) {
        var logicalCol = col + rowOffset;
        var label = rows[row][col];
        var pc = NOTE_PC[label];
        var rowsFromBottom = rows.length - 1 - row;
        var rowStartMidi = EXQUIS_BOTTOM_LEFT_MIDI;
        for (var step = 0; step < rowsFromBottom; step++) {
          rowStartMidi += step % 2 === 0 ? 4 : 3;
        }
        var midi = rowStartMidi + col;
        var x = (80 + logicalCol * CELL_W) * scale;
        var y = (76 + row * VERTICAL_ROW_STEP) * scale;
        if (state.orientation === 'horizontal') {
          x = baseWidth - (38 + row * ROW_STEP) * scale;
          y = (34 + logicalCol * CELL_W) * scale;
        }
        var dx = x - cx;
        var dy = y - cy;
        var rx = x;
        var ry = y;
        if (rotation === 90) {
          rx = rcx - dy;
          ry = rcy + dx;
        } else if (rotation === 180) {
          rx = rcx - dx;
          ry = rcy - dy;
        } else if (rotation === 270) {
          rx = rcx + dy;
          ry = rcy - dx;
        }
        cells.push({
          id: 'r' + row + 'c' + col,
          row: row,
          col: col,
          label: label,
          x: rx,
          y: ry,
          midi: midi,
          pc: pc
        });
      }
    }
    return cells;
  }

  function centerScore(cell) {
    var width = state.orientation === 'horizontal' ? SURFACE_HORIZONTAL_W : SURFACE_W;
    var height = SURFACE_H;
    if (state.rotation === 90 || state.rotation === 270) {
      var tmp = width;
      width = height;
      height = tmp;
    }
    var dx = (cell.x - width / 2) / width;
    var dy = (cell.y - height / 2) / height;
    return Math.sqrt(dx * dx + dy * dy);
  }

  function rootCandidates(cells) {
    var preferredRootMidi = 48 + state.tonicPc;
    return cells.filter(function(cell) {
      return cell.pc === state.tonicPc;
    }).sort(function(a, b) {
      return Math.abs(a.midi - preferredRootMidi) - Math.abs(b.midi - preferredRootMidi) || centerScore(a) - centerScore(b) || a.midi - b.midi;
    });
  }

  function selectedRoot(cells) {
    var roots = rootCandidates(cells);
    if (!roots.length) return null;
    for (var i = 0; i < roots.length; i++) {
      if (roots[i].id === state.rootCellId) return roots[i];
    }
    state.rootCellId = roots[0].id;
    return roots[0];
  }

  function renderRootOptions(cells) {
    if (!els.root) return;
    var roots = rootCandidates(cells);
    clearChildren(els.root);
    for (var i = 0; i < roots.length; i++) {
      var option = document.createElement('option');
      option.value = roots[i].id;
      option.textContent = noteName(roots[i].midi) + octave(roots[i].midi) + ' / row ' + (roots[i].row + 1) + ', key ' + (roots[i].col + 1);
      els.root.appendChild(option);
    }
    if (roots.length) {
      if (!roots.some(function(root) { return root.id === state.rootCellId; })) state.rootCellId = roots[0].id;
      els.root.value = state.rootCellId;
    }
  }

  function isScalePc(pc, scale) {
    var rel = mod(pc - state.tonicPc, 12);
    for (var i = 0; i < scale.intervals.length; i++) {
      if (scale.intervals[i] === rel) return true;
    }
    return false;
  }

  function logicalColumn(cell) {
    return cell.col + (ROW_COUNTS[cell.row] === 5 ? 0.5 : 0);
  }

  function chainOffset(cell, anchor) {
    return Math.round((logicalColumn(cell) - logicalColumn(anchor)) * 2);
  }

  function isInnerChainCell(cell, anchor) {
    var offset = chainOffset(cell, anchor);
    if (mod(cell.row - anchor.row, 2) === 0) return offset === 0 || offset === -2;
    return offset === -1 || offset === 1;
  }

  function chainLane(cell, anchor) {
    if (!isInnerChainCell(cell, anchor)) return '';
    var offset = chainOffset(cell, anchor);
    if (mod(cell.row - anchor.row, 2) === 0) return offset === 0 ? '0' : '1';
    return offset === 1 ? '0' : '1';
  }

  function getLitPracticeCells(cells, scale, root) {
    var lit = {};
    if (!root) return lit;
    if (state.tonicPc === 0 && state.scaleId === 'ionian') {
      DEFAULT_C_MAJOR_LED_IDS.forEach(function(id) {
        lit[id] = id === root.id ? '0' : '';
      });
      var byDefaultRow = {};
      DEFAULT_C_MAJOR_LED_IDS.forEach(function(id) {
        for (var c = 0; c < cells.length; c++) {
          if (cells[c].id === id) {
            if (!byDefaultRow[cells[c].row]) byDefaultRow[cells[c].row] = [];
            byDefaultRow[cells[c].row].push(cells[c]);
            break;
          }
        }
      });
      Object.keys(byDefaultRow).forEach(function(rowKey) {
        byDefaultRow[rowKey].sort(function(a, b) { return logicalColumn(a) - logicalColumn(b); });
        for (var d = 0; d < byDefaultRow[rowKey].length; d++) {
          lit[byDefaultRow[rowKey][d].id] = String(d);
        }
      });
      return lit;
    }
    var rootColumn = logicalColumn(root);
    var byRow = {};
    for (var i = 0; i < cells.length; i++) {
      if (!isScalePc(cells[i].pc, scale)) continue;
      if (!byRow[cells[i].row]) byRow[cells[i].row] = [];
      byRow[cells[i].row].push(cells[i]);
    }
    Object.keys(byRow).forEach(function(rowKey) {
      byRow[rowKey].sort(function(a, b) {
        return Math.abs(logicalColumn(a) - rootColumn) - Math.abs(logicalColumn(b) - rootColumn) || a.col - b.col;
      });
      for (var j = 0; j < Math.min(2, byRow[rowKey].length); j++) {
        lit[byRow[rowKey][j].id] = true;
      }
    });
    if (!lit[root.id]) lit[root.id] = true;
    var laneRows = {};
    Object.keys(lit).forEach(function(id) {
      for (var k = 0; k < cells.length; k++) {
        if (cells[k].id === id) {
          if (!laneRows[cells[k].row]) laneRows[cells[k].row] = [];
          laneRows[cells[k].row].push(cells[k]);
          break;
        }
      }
    });
    Object.keys(laneRows).forEach(function(rowKey) {
      laneRows[rowKey].sort(function(a, b) { return logicalColumn(a) - logicalColumn(b); });
      for (var l = 0; l < laneRows[rowKey].length; l++) {
        lit[laneRows[rowKey][l].id] = String(l);
      }
    });
    if (lit[root.id] === true) {
      lit[root.id] = '0';
    }
    return lit;
  }

  function bestCellForTarget(cells, pc, targetMidi, anchor) {
    var best = null;
    var bestScore = Infinity;
    for (var i = 0; i < cells.length; i++) {
      if (cells[i].pc !== pc) continue;
      var distance = Math.abs(cells[i].midi - targetMidi) * 4;
      var spatial = anchor ? (Math.abs(cells[i].row - anchor.row) + Math.abs(cells[i].col - anchor.col)) : centerScore(cells[i]) * 10;
      var chainPenalty = anchor && !isInnerChainCell(cells[i], anchor) ? 100 : 0;
      var score = chainPenalty + distance + spatial;
      if (score < bestScore) {
        best = cells[i];
        bestScore = score;
      }
    }
    return best;
  }

  function getPracticePath(cells, scale) {
    var root = selectedRoot(cells);
    if (!root) return [];
    var path = [];
    for (var d = 0; d < scale.intervals.length; d++) {
      var interval = scale.intervals[d];
      var targetMidi = root.midi + interval;
      var pc = mod(state.tonicPc + interval, 12);
      var cell = interval === 0 ? root : bestCellForTarget(cells, pc, targetMidi, root);
      if (cell) {
        var pathCell = {};
        Object.keys(cell).forEach(function(key) { pathCell[key] = cell[key]; });
        pathCell.midi = targetMidi;
        path.push(pathCell);
      }
    }
    path.push({
      id: root.id + '-octave',
      row: root.row,
      col: root.col,
      x: root.x,
      y: root.y,
      midi: root.midi + 12,
      pc: root.pc,
      virtual: true
    });
    return path;
  }

  function getScaleDegree(cell, scale) {
    var rel = mod(cell.pc - state.tonicPc, 12);
    for (var i = 0; i < scale.intervals.length; i++) {
      if (scale.intervals[i] === rel) return i + 1;
    }
    return '';
  }

  function cellKey(cell) {
    return cell ? cell.id.replace('-octave', '') : '';
  }

  function expectedCell() {
    if (!currentPath.length) return null;
    return currentPath[mod(state.step, currentPath.length)];
  }

  function getFieldBounds(cells, scale) {
    scale = scale || 1;
    var cellH = CELL_H * scale;
    var minX = Infinity;
    var maxX = -Infinity;
    var minY = Infinity;
    var maxY = -Infinity;
    for (var i = 0; i < cells.length; i++) {
      minX = Math.min(minX, cells[i].x - cellH / 2);
      maxX = Math.max(maxX, cells[i].x + cellH / 2);
      minY = Math.min(minY, cells[i].y - cellH / 2);
      maxY = Math.max(maxY, cells[i].y + cellH / 2);
    }
    return {
      left: minX,
      right: maxX,
      top: minY,
      bottom: maxY,
      width: maxX - minX,
      height: maxY - minY
    };
  }

  function getKeyboardAvailableSpace() {
    if (!els || !els.keyboard) return { width: 0, height: 0 };
    var stage = els.keyboard.closest('.stage-panel');
    var header = stage ? stage.querySelector('.stage-header') : null;
    if (!stage || !stage.getBoundingClientRect) return { width: 0, height: 0 };
    var stageBox = stage.getBoundingClientRect();
    var headerBox = header && header.getBoundingClientRect ? header.getBoundingClientRect() : { bottom: stageBox.top };
    return {
      width: Math.max(0, stageBox.width - 20),
      height: Math.max(0, stageBox.bottom - headerBox.bottom - 18)
    };
  }

  function getKeyboardScale(baseWidth, baseHeight) {
    var available = getKeyboardAvailableSpace();
    if (!available.width || !available.height) return 1;
    return Math.max(1, Math.min(1.9, available.width / baseWidth, available.height / baseHeight));
  }

  function findCellByMidi(cells, midi) {
    var best = null;
    var bestScore = Infinity;
    for (var i = 0; i < cells.length; i++) {
      if (cells[i].midi === midi) {
        var score = centerScore(cells[i]);
        var root = selectedRoot(cells);
        if (root) {
          score += (Math.abs(cells[i].row - root.row) + Math.abs(cells[i].col - root.col)) * 0.01;
        }
        if (score < bestScore) {
          best = cells[i];
          bestScore = score;
        }
      }
    }
    return best;
  }

  function noteLabelFromMidi(midi) {
    return noteName(midi) + octave(midi);
  }

  function displayMidiFromRaw(rawMidi) {
    return rawMidi;
  }

  function setFeedback(message, kind) {
    state.feedback = message;
    state.feedbackKind = kind || 'neutral';
  }

  function updateCalibrationStats() {
    var verified = Object.keys(state.calibrated).length;
    var mismatched = Object.keys(state.mismatched).length;
    els.calibrationStats.textContent = verified + ' verified / ' + mismatched + ' mismatched';
  }

  function getHeldInfoForCell(cell) {
    var info = { level: 0, exact: false };
    Object.keys(state.heldNotes).forEach(function(key) {
      var held = state.heldNotes[key];
      if (held && held.midi === cell.midi && held.cellId === cell.id) {
        var level = held.pressure || held.velocity || 0;
        info.exact = true;
        info.level = Math.max(info.level, level);
      }
    });
    return info;
  }

  function releaseMidiNote(rawMidi, channel) {
    var midi = displayMidiFromRaw(rawMidi);
    var key = voiceKey(channel, midi);
    var held = state.heldNotes[key];
    var voice = midiVoices[key];
    if (!held && !voice) {
      state.midiActivity = 'Activity: stale note-off ' + noteLabelFromMidi(midi);
      logEvent('midi', 'note-off ignored stale ' + noteLabelFromMidi(midi) + ' midi=' + midi + ' raw=' + rawMidi + ' channel=' + (channel + 1));
      render();
      return;
    }
    delete state.heldNotes[key];
    if (channel !== null && state.channelNotes[channel] === midi) {
      delete state.channelNotes[channel];
    }
    releaseMidiVoice(key, false);
    updateSsliExpressionFromHeldNotes();
    if (state.activeMidiCellId && (!held || state.activeMidiCellId === held.cellId)) {
      state.activeMidiCellId = '';
      state.activeMidiPc = null;
      state.rawMidiFlash = false;
      if (midiHitTimer) window.clearTimeout(midiHitTimer);
    }
    state.midiActivity = 'Activity: note-off ' + noteLabelFromMidi(midi);
    logEvent('midi', 'note-off ' + noteLabelFromMidi(midi) + ' midi=' + midi + ' raw=' + rawMidi + ' channel=' + (channel + 1));
    render();
  }

  function updateMidiPressure(midi, pressure, source, channel) {
    var key = voiceKey(channel, midi);
    var held = state.heldNotes[key];
    if (!held) return;
    held.pressure = Math.max(0, Math.min(127, pressure));
    updateMidiVoicePressure(key, held.pressure);
    state.midiActivity = 'Activity: ' + source + ' ' + noteLabelFromMidi(midi) + ' pressure ' + pressure;
    logEvent('midi', source + ' ' + noteLabelFromMidi(midi) + ' pressure=' + pressure);
    render();
  }

  function handleMidiNote(rawMidi, velocity, channel) {
    var midi = displayMidiFromRaw(rawMidi);
    var cells = makeGrid();
    var expected = expectedCell();
    var expectedKey = cellKey(expected);
    var hitCell = findCellByMidi(cells, midi);
    state.lastMidi = { midi: midi, velocity: velocity, cellId: hitCell ? hitCell.id : '' };
    state.activeMidiCellId = hitCell ? hitCell.id : '';
    state.activeMidiPc = mod(midi, 12);
    state.lastMidiCellId = '';
    state.lastMidiPc = null;
    state.rawMidiFlash = true;
    state.lastMidiAt = Date.now();
    state.midiActivity = 'Activity: note-on ' + noteLabelFromMidi(midi) + ' velocity ' + velocity;
    var heldKey = voiceKey(channel, midi);
    if (channel !== null && typeof state.channelNotes[channel] === 'number' && state.channelNotes[channel] !== midi) {
      var previousMidi = state.channelNotes[channel];
      var previousKey = voiceKey(channel, previousMidi);
      delete state.heldNotes[previousKey];
      releaseMidiVoice(previousKey, true);
      logEvent('audio', 'released previous channel voice ' + noteLabelFromMidi(previousMidi) + ' before ' + noteLabelFromMidi(midi));
    }
    state.heldNotes[heldKey] = {
      midi: midi,
      rawMidi: rawMidi,
      pc: mod(midi, 12),
      velocity: velocity,
      pressure: velocity,
      cellId: hitCell ? hitCell.id : '',
      channel: channel
    };
    if (channel !== null) state.channelNotes[channel] = midi;
    startMidiVoice(heldKey, midi, velocity);
    logEvent('midi', 'note-on ' + noteLabelFromMidi(midi) + ' midi=' + midi + ' raw=' + rawMidi + ' velocity=' + velocity + ' channel=' + (channel + 1) + ' match=' + (hitCell ? hitCell.id : 'pitch-only'));

    if (expected && mod(midi, 12) === expected.pc) {
      state.correctCount += 1;
      state.streak += 1;
      state.calibrated[expectedKey] = {
        expectedMidi: expected.midi,
        receivedMidi: midi,
        at: state.lastMidiAt
      };
      delete state.mismatched[expectedKey];
      setFeedback('Correct: ' + noteLabelFromMidi(midi) + ' matches the current target.', 'good');
      if (state.autoAdvance) {
        window.setTimeout(function() {
          state.step += 1;
          render();
        }, 220);
      }
    } else if (expected) {
      state.missCount += 1;
      state.streak = 0;
      state.mismatched[expectedKey] = {
        expectedMidi: expected.midi,
        receivedMidi: midi,
        at: state.lastMidiAt
      };
      setFeedback('Not this one: heard ' + noteLabelFromMidi(midi) + ', target is ' + noteLabelFromMidi(expected.midi) + '.', 'bad');
    }

    if (midiHitTimer) window.clearTimeout(midiHitTimer);
    midiHitTimer = window.setTimeout(function() {
      state.activeMidiCellId = '';
      state.activeMidiPc = null;
      state.lastMidiCellId = '';
      state.lastMidiPc = null;
      state.rawMidiFlash = false;
      render();
    }, 900);
    if (midiActivityTimer) window.clearTimeout(midiActivityTimer);
    midiActivityTimer = window.setTimeout(function() {
      state.midiActivity = 'Activity: listening';
      render();
    }, 1400);
    render();
  }

  function onMidiMessage(event) {
    var data = event.data;
    if (!data || data.length < 2) return;
    var status = data[0] & 0xF0;
    var channel = data[0] & 0x0F;
    var midi = data[1];
    var velocity = data.length > 2 ? data[2] : 0;
    var isNoteOn = status === 0x90 && velocity > 0;
    var isNoteOff = status === 0x80 || (status === 0x90 && velocity === 0);
    if (isNoteOn) {
      handleMidiNote(midi, velocity, channel);
    } else if (isNoteOff) {
      releaseMidiNote(midi, channel);
    } else if (status === 0xA0) {
      updateMidiPressure(displayMidiFromRaw(midi), velocity, 'poly-aftertouch', channel);
    } else if (status === 0xD0) {
      var channelMidi = state.channelNotes[channel];
      if (typeof channelMidi === 'number') updateMidiPressure(channelMidi, midi, 'channel-pressure', channel);
    }
  }

  function midiInputLabel(input) {
    var name = input && input.name ? input.name : 'Unnamed MIDI input';
    var manufacturer = input && input.manufacturer ? input.manufacturer : '';
    return manufacturer && name.indexOf(manufacturer) < 0 ? name + ' (' + manufacturer + ')' : name;
  }

  function getMidiInputs(access) {
    var inputs = [];
    if (!access || !access.inputs) return inputs;
    access.inputs.forEach(function(input) {
      inputs.push(input);
    });
    inputs.sort(function(a, b) {
      return midiInputLabel(a).localeCompare(midiInputLabel(b));
    });
    return inputs;
  }

  function chooseMidiInput(access) {
    var chosen = null;
    var inputs = getMidiInputs(access);
    for (var i = 0; i < inputs.length; i++) {
      var input = inputs[i];
      var name = ((input.name || '') + ' ' + (input.manufacturer || '')).toLowerCase();
      if (state.selectedMidiId && input.id === state.selectedMidiId) {
        chosen = input;
        break;
      }
      if (!chosen || name.indexOf('exquis') >= 0 || name.indexOf('intuitive') >= 0) {
        chosen = input;
      }
    }
    return chosen;
  }

  function disconnectMidiInput() {
    if (midiInput) midiInput.onmidimessage = null;
    midiInput = null;
  }

  function connectMidiInput(input) {
    disconnectMidiInput();
    midiInput = input;
    if (midiInput) {
      midiInput.onmidimessage = onMidiMessage;
      state.selectedMidiId = midiInput.id || '';
      state.midiStatus = 'MIDI input: ' + midiInputLabel(midiInput);
      state.midiActivity = 'Activity: listening';
      logEvent('midi', 'listening on ' + midiInputLabel(midiInput) + ' id=' + (midiInput.id || 'unknown'));
      setFeedback('MIDI coach is listening. Play the highlighted target.', 'neutral');
    }
  }

  function refreshMidiInputs(access) {
    var inputs = getMidiInputs(access);
    state.midiInputs = inputs.map(function(input) {
      return {
        id: input.id || midiInputLabel(input),
        label: midiInputLabel(input),
        state: input.state || '',
        connection: input.connection || ''
      };
    });
    if (inputs.length && !state.selectedMidiId) {
      var preferred = chooseMidiInput(access);
      state.selectedMidiId = preferred && preferred.id ? preferred.id : inputs[0].id;
    }
    return inputs;
  }

  function enableMidi() {
    if (!navigator.requestMIDIAccess) {
      state.midiStatus = 'Web MIDI is not available in this browser.';
      setFeedback('Use Chrome or Edge for MIDI coaching.', 'bad');
      render();
      return;
    }
    navigator.requestMIDIAccess({ sysex: false }).then(function(access) {
      midiAccess = access;
      midiAccess.onstatechange = function() {
        refreshMidiInputs(midiAccess);
        if (!midiInput || state.selectedMidiId) {
          connectMidiInput(chooseMidiInput(midiAccess));
        }
        render();
      };
      var inputs = refreshMidiInputs(access);
      if (inputs.length) {
        connectMidiInput(chooseMidiInput(access));
        logEvent('midi', 'visible inputs: ' + inputs.map(midiInputLabel).join(', '));
      } else {
        disconnectMidiInput();
        state.midiStatus = 'No MIDI input found.';
        logEvent('midi', 'no inputs visible to browser');
        setFeedback('No MIDI input found. Confirm the Exquis is connected and not held by another app.', 'bad');
      }
      render();
    }).catch(function(err) {
      state.midiStatus = 'MIDI permission denied.';
      logEvent('midi', 'permission/access failed: ' + (err && err.message ? err.message : err));
      setFeedback(err && err.message ? err.message : 'MIDI permission denied.', 'bad');
      render();
    });
  }

  function clearChildren(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function appendOptions(select, options, valueProp, labelProp) {
    clearChildren(select);
    for (var i = 0; i < options.length; i++) {
      var option = document.createElement('option');
      option.value = typeof valueProp === 'function' ? valueProp(options[i]) : options[i][valueProp];
      option.textContent = typeof labelProp === 'function' ? labelProp(options[i]) : options[i][labelProp];
      select.appendChild(option);
    }
  }

  function renderSoundSelectorOptions() {
    var engines = getSoundEngines();
    appendOptions(els.soundEngine, engines.map(function(engine) { return { id: engine, label: engine }; }), 'id', 'label');
    if (engines.indexOf(state.soundEngine) < 0) state.soundEngine = engines[0] || '';
    els.soundEngine.value = state.soundEngine;

    var categories = getSoundCategories(state.soundEngine);
    appendOptions(els.soundCategory, categories.map(function(category) { return { id: category, label: category }; }), 'id', 'label');
    if (categories.indexOf(state.soundCategory) < 0) state.soundCategory = categories[0] || '';
    els.soundCategory.value = state.soundCategory;

    var presets = getSoundPresetsFor(state.soundEngine, state.soundCategory);
    appendOptions(els.soundPreset, presets, function(preset) { return state.soundEngine + '::' + preset.name; }, function(preset) { return preset.name; });
    if (!presets.some(function(preset) { return state.soundPresetId === state.soundEngine + '::' + preset.name; }) && presets.length) {
      state.soundPresetId = state.soundEngine + '::' + presets[0].name;
    }
    els.soundPreset.value = state.soundPresetId;
  }

  function renderFxSelectorOptions() {
    var categories = getFxCategories();
    appendOptions(els.fxCategory, categories.map(function(category) { return { id: category, label: category }; }), 'id', 'label');
    if (categories.indexOf(state.fxCategory) < 0) state.fxCategory = categories[0] || '';
    els.fxCategory.value = state.fxCategory;

    var presets = getFxPresetsFor(state.fxCategory);
    appendOptions(els.fxPreset, presets, 'id', 'label');
    if (!presets.some(function(preset) { return preset.id === state.fxPresetId; }) && presets.length) {
      state.fxPresetId = presets[0].id;
    }
    els.fxPreset.value = state.fxPresetId;
  }

  function renderOptions() {
    var i;
    for (i = 0; i < TONICS.length; i++) {
      var to = document.createElement('option');
      to.value = String(TONICS[i].pc);
      to.textContent = TONICS[i].name;
      els.tonic.appendChild(to);
    }
    for (i = 0; i < SCALE_KEYS.length; i++) {
      var scaleData = SSLI_MODES[SCALE_KEYS[i]];
      var so = document.createElement('option');
      so.value = SCALE_KEYS[i];
      so.textContent = scaleData && scaleData.name ? scaleData.name : SCALE_KEYS[i];
      els.scale.appendChild(so);
    }
    for (i = 0; i < STRATEGIES.length; i++) {
      var fo = document.createElement('option');
      fo.value = STRATEGIES[i].id;
      fo.textContent = STRATEGIES[i].name;
      els.strategy.appendChild(fo);
    }
    syncSoundSelectorsFromPreset();
    syncFxSelectorsFromPreset();
    renderSoundSelectorOptions();
    renderFxSelectorOptions();
  }

  function render() {
    var logicCells = makeGrid();
    var cells = logicCells;
    var scale = getScale();
    var strategy = getStrategy();
    var fingers = getStrategyFingers(strategy);
    renderRootOptions(logicCells);
    var path = getPracticePath(logicCells, scale);
    currentPath = path;
    var current = path.length ? path[mod(state.step, path.length)] : null;
    var rootId = state.rootCellId;
    var rootCell = null;
    for (i = 0; i < cells.length; i++) {
      if (cells[i].id === rootId) {
        rootCell = cells[i];
        break;
      }
    }
    var litPracticeById = getLitPracticeCells(cells, scale, rootCell);
    var pathById = {};
    var pathIndexById = {};
    var pathMidiById = {};
    var fingerById = {};
    var i;

    state.step = path.length ? mod(state.step, path.length) : 0;
    for (i = 0; i < path.length; i++) {
      pathById[path[i].id.replace('-octave', '')] = true;
      if (typeof pathIndexById[path[i].id.replace('-octave', '')] !== 'number') {
        pathIndexById[path[i].id.replace('-octave', '')] = i;
      }
      if (typeof pathMidiById[path[i].id.replace('-octave', '')] !== 'number') {
        pathMidiById[path[i].id.replace('-octave', '')] = path[i].midi;
      }
      if (!fingerById[path[i].id.replace('-octave', '')]) {
        fingerById[path[i].id.replace('-octave', '')] = fingers[i % fingers.length];
      }
    }

    clearChildren(els.keyboard);
    els.keyboard.className = 'keyboard keyboard-' + state.orientation + (state.rotation === 90 || state.rotation === 270 ? ' keyboard-rotated-sideways' : '');
    els.keyboard.setAttribute('data-rotation', String(mod(state.rotation, 360)));
    var baseFieldBounds = getFieldBounds(logicCells);
    var baseKeyboardWidth = Math.round(baseFieldBounds.width + 130);
    var baseKeyboardHeight = Math.round(baseFieldBounds.height + 48);
    var layoutScale = getKeyboardScale(baseKeyboardWidth, baseKeyboardHeight);
    cells = makeGrid(layoutScale);
    var fieldBounds = getFieldBounds(cells, layoutScale);
    var keyboardWidth = Math.round(baseKeyboardWidth * layoutScale);
    var keyboardHeight = Math.round(baseKeyboardHeight * layoutScale);
    var shiftX = (keyboardWidth - fieldBounds.width) / 2 - fieldBounds.left;
    var shiftY = (keyboardHeight - fieldBounds.height) / 2 - fieldBounds.top;
    els.keyboard.style.width = keyboardWidth + 'px';
    els.keyboard.style.height = keyboardHeight + 'px';
    els.keyboard.style.minHeight = keyboardHeight + 'px';
    els.keyboard.style.setProperty('--key-w', (CELL_W * layoutScale).toFixed(3) + 'px');
    els.keyboard.style.setProperty('--key-h', (CELL_H * layoutScale).toFixed(3) + 'px');
    els.keyboard.style.setProperty('--surface-w', Math.round(fieldBounds.width + 28) + 'px');
    els.keyboard.style.setProperty('--surface-h', Math.round(fieldBounds.height + 28) + 'px');
    var supportedRotationLabel = state.rotation === 0 ? 180 : 0;
    els.rotateSurface.textContent = 'Rotate ' + supportedRotationLabel;
    els.rotateSurface.setAttribute('aria-label', 'Rotate surface to ' + supportedRotationLabel + ' degrees');
    for (i = 0; i < cells.length; i++) {
      var cell = cells[i];
      var inPath = !!pathById[cell.id];
      var displayMidi = inPath && typeof pathMidiById[cell.id] === 'number' ? pathMidiById[cell.id] : cell.midi;
      var hardwareLit = state.view === 'practice' && !!litPracticeById[cell.id];
      var inScale = state.view === 'practice' ? inPath : isScalePc(cell.pc, scale);
      var isTonic = cell.pc === state.tonicPc;
      var isCurrent = current && current.id.replace('-octave', '') === cell.id;
      var heldInfo = getHeldInfoForCell(cell);
      var heldLevel = heldInfo.level;
      var heldPressure = heldLevel / 127;
      var key = document.createElement('button');
      var classes = ['key'];
      if (hardwareLit) classes.push('hardware-lit');
      if (inScale) classes.push('in-scale');
      if (inPath && state.view === 'practice') classes.push('in-path');
      if (isTonic) classes.push('tonic');
      if (isCurrent) classes.push('current');
      if (state.view === 'calibration' && isCurrent) classes.push('calibration-target');
      if (heldLevel > 0 && heldInfo.exact) classes.push('midi-held');
      if (state.rawMidiFlash && state.activeMidiCellId === cell.id) classes.push('midi-hit');
      if (!state.rawMidiFlash && state.lastMidiCellId === cell.id) classes.push('midi-last');
      if (state.rawMidiFlash && state.activeMidiPc === null && isCurrent) classes.push('raw-midi-hit');
      if (state.calibrated[cell.id]) classes.push('calibrated');
      if (state.mismatched[cell.id]) classes.push('mismatch');
      if (state.view === 'practice' && !inPath && !hardwareLit) classes.push('dimmed');
      if (state.view === 'scale' && !inScale) classes.push('dimmed');
      if (state.view === 'calibration' && !isCurrent) classes.push('dimmed');
      key.type = 'button';
      key.className = classes.join(' ');
      key.style.left = (cell.x + shiftX) + 'px';
      key.style.top = (cell.y + shiftY) + 'px';
      if (heldLevel > 0) {
        key.style.setProperty('--midi-pressure', String(Math.max(0.08, heldPressure)));
        key.style.setProperty('--midi-level', Math.round(35 + heldPressure * 65) + '%');
      }
      key.setAttribute('data-testid', 'exquis-key');
      key.setAttribute('data-cell-id', cell.id);
      key.setAttribute('data-midi', String(displayMidi));
      key.setAttribute('data-pc', String(cell.pc));
      if (typeof pathIndexById[cell.id] === 'number') key.setAttribute('data-path-index', String(pathIndexById[cell.id]));
      if (rootCell) {
        key.setAttribute('data-chain-offset', String(chainOffset(cell, rootCell)));
        key.setAttribute('data-chain-lane', hardwareLit ? String(litPracticeById[cell.id]) : chainLane(cell, rootCell));
      }
      key.setAttribute('aria-label', cell.label + octave(displayMidi));
      key.addEventListener('pointerdown', (function(cellValue) {
        return function() {
          pressUiKey(cellValue, 96);
        };
      })(cell));
      key.addEventListener('pointerup', (function(cellValue) {
        return function() {
          releaseUiKey(cellValue);
        };
      })(cell));
      key.addEventListener('pointercancel', (function(cellValue) {
        return function() {
          releaseUiKey(cellValue);
        };
      })(cell));
      key.addEventListener('pointerleave', (function(cellValue) {
        return function(event) {
          if (event.buttons) releaseUiKey(cellValue);
        };
      })(cell));
      key.innerHTML = '<span class="key-label"><span class="note">' + cell.label + '</span><span class="octave">' + octave(displayMidi) + '</span></span>';
      if (inPath && state.view === 'practice') {
        var degree = document.createElement('span');
        degree.className = 'degree-badge';
        degree.textContent = String(getScaleDegree(cell, scale));
        key.appendChild(degree);
        var finger = document.createElement('span');
        finger.className = 'finger';
        finger.textContent = String(fingerById[cell.id]);
        key.appendChild(finger);
      }
      els.keyboard.appendChild(key);
    }

    els.title.textContent = getTonicName() + ' ' + scale.name;
    els.subtitle.textContent = (state.hand === 'right' ? 'Right' : 'Left') + ' hand: ' + strategy.name;
    els.fingerRule.textContent = getHandRule(strategy);
    els.stepReadout.textContent = path.length ? String(state.step + 1) + ' / ' + path.length : '0 / 0';
    els.currentNote.textContent = current ? noteName(current.midi) + octave(current.midi) : '--';
    els.currentDegree.textContent = current ? 'Scale degree ' + getScaleDegree(current, scale) : 'Scale degree --';
    els.audioStatus.textContent = state.audioStatus;
    if (els.filterCutoffValue) els.filterCutoffValue.textContent = Math.round(state.filterCutoff) + ' Hz';
    if (els.filterResonanceValue) els.filterResonanceValue.textContent = String(Math.round(state.filterResonance * 10) / 10);
    els.midiStatus.textContent = state.midiStatus;
    clearChildren(els.midiInputSelect);
    if (state.midiInputs.length) {
      for (var mi = 0; mi < state.midiInputs.length; mi++) {
        var opt = document.createElement('option');
        opt.value = state.midiInputs[mi].id;
        opt.textContent = state.midiInputs[mi].label;
        els.midiInputSelect.appendChild(opt);
      }
      els.midiInputSelect.disabled = false;
      els.midiInputSelect.value = state.selectedMidiId;
      els.midiDevices.textContent = 'Devices: ' + state.midiInputs.map(function(input) {
        var details = [input.state, input.connection].filter(Boolean).join('/');
        return details ? input.label + ' [' + details + ']' : input.label;
      }).join(', ');
    } else {
      var emptyOpt = document.createElement('option');
      emptyOpt.value = '';
      emptyOpt.textContent = midiAccess ? 'No MIDI inputs found' : 'No inputs scanned';
      els.midiInputSelect.appendChild(emptyOpt);
      els.midiInputSelect.disabled = true;
      els.midiDevices.textContent = midiAccess ? 'Devices: none visible to browser' : 'Devices: not scanned';
    }
    els.lastMidi.textContent = state.lastMidi ? 'Last input: ' + noteLabelFromMidi(state.lastMidi.midi) + ' velocity ' + state.lastMidi.velocity : 'Last input: --';
    els.midiActivity.className = state.lastMidi ? 'feedback-live' : 'feedback-neutral';
    els.midiActivity.textContent = state.midiActivity;
    els.coachFeedback.className = 'feedback-' + state.feedbackKind;
    els.coachFeedback.textContent = state.feedback;
    els.drillScore.textContent = 'Score: ' + state.correctCount + ' correct / ' + state.missCount + ' missed / streak ' + state.streak;
    updateCalibrationStats();
    if (state.view === 'calibration') {
      els.assumptionText.className = 'calibration-note';
      els.assumptionText.textContent = 'Calibration preview: this will become the hardware-matching mode. Press Play to hear the target, then compare it with the matching physical Exquis button.';
    } else {
      els.assumptionText.className = '';
      els.assumptionText.textContent = 'This first build uses a documented Exquis-style model: horizontal semitones and vertical thirds. It is meant for fingering exploration, then calibration against the physical keyboard.';
    }
  }

  function bindEvents() {
    els.tonic.addEventListener('change', function() {
      state.tonicPc = parseInt(els.tonic.value, 10) || 0;
      state.rootCellId = '';
      state.step = 0;
      render();
    });
    els.root.addEventListener('change', function() {
      state.rootCellId = els.root.value;
      state.step = 0;
      render();
    });
    els.scale.addEventListener('change', function() {
      state.scaleId = els.scale.value;
      state.step = 0;
      render();
    });
    els.hand.addEventListener('change', function() {
      state.hand = els.hand.value;
      render();
    });
    els.strategy.addEventListener('change', function() {
      state.strategyId = els.strategy.value;
      render();
    });
    els.view.addEventListener('change', function() {
      state.view = els.view.value;
      render();
    });
    els.orientation.addEventListener('change', function() {
      state.orientation = els.orientation.value;
      state.rootCellId = '';
      render();
    });
    els.rotateSurface.addEventListener('click', function() {
      state.rotation = state.rotation === 0 ? 180 : 0;
      state.rootCellId = '';
      logEvent('ui', 'surface rotation ' + state.rotation);
      render();
    });
    els.tone.addEventListener('change', function() {
      state.tone = els.tone.value;
    });
    els.soundEngine.addEventListener('change', function() {
      state.soundEngine = els.soundEngine.value;
      state.soundCategory = '';
      state.soundPresetId = '';
      invalidateSsliPresetCache();
      renderSoundSelectorOptions();
      logEvent('audio', 'sound engine ' + state.soundEngine);
    });
    els.soundCategory.addEventListener('change', function() {
      state.soundCategory = els.soundCategory.value;
      state.soundPresetId = '';
      invalidateSsliPresetCache();
      renderSoundSelectorOptions();
      logEvent('audio', 'sound category ' + state.soundCategory);
    });
    els.soundPreset.addEventListener('change', function() {
      state.soundPresetId = els.soundPreset.value;
      invalidateSsliPresetCache();
      syncSoundSelectorsFromPreset();
      applySelectedSsliPreset();
      logEvent('audio', 'sound preset ' + state.soundPresetId);
    });
    els.fxCategory.addEventListener('change', function() {
      state.fxCategory = els.fxCategory.value;
      state.fxPresetId = '';
      state.fxDirty = true;
      renderFxSelectorOptions();
      applySelectedSsliFxChain();
      if (audioCtx) rebuildFxBus(audioCtx);
      logEvent('audio', 'FX category ' + state.fxCategory);
    });
    els.fxPreset.addEventListener('change', function() {
      state.fxPresetId = els.fxPreset.value;
      state.fxDirty = true;
      syncFxSelectorsFromPreset();
      applySelectedSsliFxChain();
      if (audioCtx) rebuildFxBus(audioCtx);
      logEvent('audio', 'FX preset ' + state.fxPresetId);
    });
    els.filterType.addEventListener('change', function() {
      state.filterType = els.filterType.value;
      state.filterDirty = true;
      applySelectedSsliFilter();
      logEvent('audio', 'filter type ' + state.filterType);
    });
    els.filterCutoff.addEventListener('input', function() {
      state.filterCutoff = parseFloat(els.filterCutoff.value) || 2200;
      state.filterDirty = true;
      if (els.filterCutoffValue) els.filterCutoffValue.textContent = Math.round(state.filterCutoff) + ' Hz';
      applySelectedSsliFilter();
    });
    els.filterResonance.addEventListener('input', function() {
      state.filterResonance = parseFloat(els.filterResonance.value) || 0.8;
      state.filterDirty = true;
      if (els.filterResonanceValue) els.filterResonanceValue.textContent = String(Math.round(state.filterResonance * 10) / 10);
      applySelectedSsliFilter();
    });
    els.autoAdvance.addEventListener('change', function() {
      state.autoAdvance = els.autoAdvance.checked;
    });
    els.next.addEventListener('click', function() {
      state.step += 1;
      render();
    });
    els.prev.addEventListener('click', function() {
      state.step -= 1;
      render();
    });
    els.playStep.addEventListener('click', playCurrent);
    els.testAudio.addEventListener('click', playTestTone);
    els.playScale.addEventListener('click', playPath);
    els.enableMidi.addEventListener('click', enableMidi);
    els.resetConsole.addEventListener('click', resetConsole);
    els.copyConsole.addEventListener('click', copyConsole);
    els.exitConsole.addEventListener('click', exitConsole);
    window.addEventListener('pointerup', releaseAllUiKeys);
    window.addEventListener('blur', releaseAllUiKeys);
    window.addEventListener('resize', function() {
      if (resizeTimer) window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(function() {
        render();
      }, 40);
    });
    els.midiInputSelect.addEventListener('change', function() {
      state.selectedMidiId = els.midiInputSelect.value;
      if (midiAccess) {
        connectMidiInput(chooseMidiInput(midiAccess));
        render();
      }
    });
    els.clearCalibration.addEventListener('click', function() {
      state.calibrated = {};
      state.mismatched = {};
      state.lastMidi = null;
      resetVisualMidi();
      state.correctCount = 0;
      state.missCount = 0;
      state.streak = 0;
      setFeedback('Session calibration cleared.', 'neutral');
      render();
    });
  }

  function init() {
    els = {
      tonic: document.getElementById('tonicSelect'),
      root: document.getElementById('rootSelect'),
      scale: document.getElementById('scaleSelect'),
      hand: document.getElementById('handSelect'),
      strategy: document.getElementById('strategySelect'),
      view: document.getElementById('viewSelect'),
      orientation: document.getElementById('orientationSelect'),
      rotateSurface: document.getElementById('rotateSurface'),
      tone: document.getElementById('toneSelect'),
      soundEngine: document.getElementById('soundEngineSelect'),
      soundCategory: document.getElementById('soundCategorySelect'),
      soundPreset: document.getElementById('soundPresetSelect'),
      fxCategory: document.getElementById('fxCategorySelect'),
      fxPreset: document.getElementById('fxPresetSelect'),
      filterType: document.getElementById('filterTypeSelect'),
      filterCutoff: document.getElementById('filterCutoff'),
      filterResonance: document.getElementById('filterResonance'),
      filterCutoffValue: document.getElementById('filterCutoffValue'),
      filterResonanceValue: document.getElementById('filterResonanceValue'),
      autoAdvance: document.getElementById('autoAdvance'),
      keyboard: document.getElementById('keyboard'),
      title: document.getElementById('stateTitle'),
      subtitle: document.getElementById('stateSubtitle'),
      fingerRule: document.getElementById('fingerRule'),
      currentNote: document.getElementById('currentNote'),
      stepReadout: document.getElementById('stepReadout'),
      currentDegree: document.getElementById('currentDegree'),
      assumptionText: document.getElementById('assumptionText'),
      next: document.getElementById('nextStep'),
      prev: document.getElementById('prevStep'),
      playStep: document.getElementById('playStep'),
      testAudio: document.getElementById('testAudio'),
      playScale: document.getElementById('playScale'),
      audioStatus: document.getElementById('audioStatus'),
      audioScope: document.getElementById('audioScope'),
      scopeReadout: document.getElementById('scopeReadout'),
      midiStatus: document.getElementById('midiStatus'),
      midiActivity: document.getElementById('midiActivity'),
      midiInputSelect: document.getElementById('midiInputSelect'),
      midiDevices: document.getElementById('midiDevices'),
      enableMidi: document.getElementById('enableMidi'),
      lastMidi: document.getElementById('lastMidi'),
      coachFeedback: document.getElementById('coachFeedback'),
      drillScore: document.getElementById('drillScore'),
      calibrationStats: document.getElementById('calibrationStats'),
      clearCalibration: document.getElementById('clearCalibration'),
      consolePanel: document.getElementById('consolePanel'),
      diagnosticLog: document.getElementById('diagnosticLog'),
      resetConsole: document.getElementById('resetConsole'),
      copyConsole: document.getElementById('copyConsole'),
      exitConsole: document.getElementById('exitConsole')
    };
    renderOptions();
    els.tonic.value = String(state.tonicPc);
    els.hand.value = state.hand;
    els.scale.value = state.scaleId;
    els.strategy.value = state.strategyId;
    els.view.value = state.view;
    els.orientation.value = state.orientation;
    els.tone.value = state.tone;
    els.soundEngine.value = state.soundEngine;
    els.soundCategory.value = state.soundCategory;
    els.soundPreset.value = state.soundPresetId;
    els.fxCategory.value = state.fxCategory;
    els.fxPreset.value = state.fxPresetId;
    els.filterType.value = state.filterType;
    els.filterCutoff.value = String(state.filterCutoff);
    els.filterResonance.value = String(state.filterResonance);
    els.autoAdvance.checked = state.autoAdvance;
    bindEvents();
    var ssliFrame = document.getElementById('ssliEngineFrame');
    if (ssliFrame) {
      ssliFrame.addEventListener('load', function() {
        renderSoundSelectorOptions();
        syncSoundSelectorsFromPreset();
        render();
        logEvent('audio', 'SSLI runtime preset API ready');
      });
    }
    render();
    drawAudioScope();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
