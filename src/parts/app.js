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
  var EXQUIS_SCALE_NUMBER_BY_ID = {
    ionian: 0,
    dorian: 1,
    mixolydian: 4,
    aeolian: 5
  };
  var EXQUIS_SCALE_ID_BY_NUMBER = {
    0: 'ionian',
    1: 'dorian',
    4: 'mixolydian',
    5: 'aeolian'
  };
  var EXQUIS_EDGE_CONTROLS = [
    { id: 'settings', zone: 'settings', kind: 'button', led: 100, label: 'Settings', detail: 'Hold: settings menu' },
    { id: 'sound', zone: 'settings', kind: 'button', led: 101, label: 'Sound', detail: 'Hold: compatibility/menu' },
    { id: 'record', zone: 'other', kind: 'button', led: 102, label: 'Record', detail: 'Action button' },
    { id: 'loop', zone: 'other', kind: 'button', led: 103, label: 'Loop', detail: 'Action button' },
    { id: 'clips', zone: 'other', kind: 'button', led: 104, label: 'Clips', detail: 'Action button' },
    { id: 'playStop', zone: 'other', kind: 'button', led: 105, label: 'Play/Stop', detail: 'MIDI clock play/stop' },
    { id: 'down', zone: 'updown', kind: 'button', led: 106, label: 'Down', detail: 'Octave down' },
    { id: 'up', zone: 'updown', kind: 'button', led: 107, label: 'Up', detail: 'Octave up' },
    { id: 'undo', zone: 'other', kind: 'button', led: 108, label: 'Undo', detail: 'Action button' },
    { id: 'redo', zone: 'other', kind: 'button', led: 109, label: 'Redo', detail: 'Action button' },
    { id: 'enc1', zone: 'encoders', kind: 'encoder', led: 110, clickCc: 21, cc: 41, label: 'Encoder 1', detail: 'CC41 / click CC21' },
    { id: 'enc2', zone: 'encoders', kind: 'encoder', led: 111, clickCc: 22, cc: 42, label: 'Encoder 2', detail: 'CC42 / root in Settings' },
    { id: 'enc3', zone: 'encoders', kind: 'encoder', led: 112, clickCc: 23, cc: 43, label: 'Encoder 3', detail: 'CC43 / scale in Settings' },
    { id: 'enc4', zone: 'encoders', kind: 'encoder', led: 113, clickCc: 24, cc: 44, label: 'Encoder 4', detail: 'CC44 / brightness/sensitivity' },
    { id: 'slider', zone: 'slider', kind: 'slider', led: 90, label: 'Slider', detail: 'Arpeggiator speed/pattern, portions 80-85' }
  ];
  var EXQUIS_EDGE_BY_CC = {};
  var EXQUIS_EDGE_BY_CLICK_CC = {};
  var EXQUIS_EDGE_BY_OFFICIAL_ID = {};
  var EXQUIS_EDGE_BY_ID = {};
  for (var edgeIndex = 0; edgeIndex < EXQUIS_EDGE_CONTROLS.length; edgeIndex++) {
    var edgeControl = EXQUIS_EDGE_CONTROLS[edgeIndex];
    EXQUIS_EDGE_BY_ID[edgeControl.id] = edgeControl;
    if (typeof edgeControl.cc === 'number') EXQUIS_EDGE_BY_CC[edgeControl.cc] = edgeControl;
    if (typeof edgeControl.clickCc === 'number') EXQUIS_EDGE_BY_CLICK_CC[edgeControl.clickCc] = edgeControl;
    EXQUIS_EDGE_BY_OFFICIAL_ID[edgeControl.led] = edgeControl;
  }
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
      id: 'wrist_pairs',
      name: 'Wrist-led pairs',
      leftFingers: [5, 4, 4, 3, 5, 4, 4, 3],
      rightFingers: [2, 3, 3, 4, 2, 3, 3, 4],
      rule: 'Pair nearby steps under one finger when it lets the wrist carry the motion. Do not lock the arm or drag pressure sideways.'
    },
    {
      id: 'natural_clusters',
      name: 'Natural clusters',
      leftFingers: [5, 4, 4, 3, 3, 2, 2, 2],
      rightFingers: [2, 3, 3, 4, 4, 5, 5, 5],
      rule: 'Start with the pinky, let ring and middle carry nearby pairs, then let the index handle the upper cluster.'
    },
    {
      id: 'position_shift',
      name: 'Position shift',
      leftFingers: [4, 3, 2, 1, 4, 3, 2, 1],
      rightFingers: [1, 2, 3, 4, 1, 2, 3, 4],
      rule: 'Use 4-3-2-1 in compact positions and move the whole hand between groups.'
    }
  ];
  var EXERCISES = [
    {
      id: 'root_octave',
      name: 'Root to octave',
      prompt: 'Play the centered root-to-octave scale path. Keep the shape on the inner two Exquis chains.'
    },
    {
      id: 'two_octaves',
      name: 'Two octaves',
      prompt: 'Continue the same Exquis chain shape through the second octave without switching into piano-style fingering.'
    },
    {
      id: 'inner_ladder',
      name: 'Inner-chain ladder',
      prompt: 'Climb the inner two chains, then reverse the same physical path back to the centered root.'
    },
    {
      id: 'root_returns',
      name: 'Root returns',
      prompt: 'Return to the centered root between every scale tone so the hand keeps its home reference.'
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
  var DEFAULT_PERFORMANCE_VOLUME = 80;
  var SSLI_NORMALIZATION_BASE_VOLUME = DEFAULT_PERFORMANCE_VOLUME;
  var SSLI_NORMALIZATION_MAX_OUTPUT_GAIN = 1;
  var SSLI_MATURE_ENGINE_NORMALIZATION = null;
  var SSLI_PRESET_NORMALIZATION = {
  };
  var SSLI_PHYSICAL_PLUCK_AUTO_DAMP_MS = 360;
  var SSLI_PHYSICAL_PLUCK_ONE_SHOT_MS = 320;
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
  var midiOutput = null;
  var midiHitTimer = null;
  var midiActivityTimer = null;
  var exquisLegacyKeepaliveTimer = null;
  var exquisLegacySyncTimer = null;
  var lastExquisLegacySyncAt = 0;
  var lastExquisLegacyKeepaliveLogAt = 0;
  var exquisLegacyNoteMapSent = false;
  var exquisSyncSuppressUntil = 0;
  var resizeTimer = null;
  var ssliPresetRetryTimer = null;
  var logs = [];
  var pendingLogs = [];
  var logFlushTimer = null;
  var midiVoices = {};
  var recentMidiNoteOffs = {};
  var pendingShortNoteReleases = {};
  var pendingShortRawReleases = {};
  var recentMidiChordNotes = [];
  var recentMidiChordTimer = null;
  var articulationQueue = [];
  var articulationFlushTimer = null;
  var articulationSequence = 0;
  var lastAppliedSsliPresetKey = '';
  var lastSsliExpressionPressure = null;
  var lastMidiPressureRenderAt = 0;
  var lastMidiPressureLogAt = 0;
  var skippedSsliExpressionUpdates = 0;
  var MIDI_VOICE_BUDGET = 12;
  var SSLI_EXPRESSION_PRESSURE_STEP = 8;
  var PHYSICAL_PRESSURE_STEP = 14;
  var PHYSICAL_PRESSURE_MIN_INTERVAL_MS = 35;
  var PHYSICAL_SIMULTANEOUS_ONSET_MS = 45;
  var PHYSICAL_UNSCALED_SIMULTANEOUS_VOICES = 2;
  var EXQUIS_MIN_MIDI_HOLD_MS = 110;
  var MATURE_SOUND_ENGINES = { subtractive: true, physical: true, fm: true };
  var state = {
    tonicPc: 0,
    rootCellId: '',
    octaveSide: 'higher',
    mode: 'practice',
    hand: 'left',
    exerciseId: 'root_octave',
    scaleId: 'ionian',
    strategyId: 'natural_clusters',
    view: 'practice',
    tone: 'soft_wurli',
    soundPresetId: 'subtractive::Wurlitzer EP',
    soundEngine: 'subtractive',
    soundCategory: 'Keys',
    showAllEngines: false,
    fxPresetId: 'dry',
    fxCategory: 'Clean / Natural',
    fxDirty: false,
    performanceVolume: DEFAULT_PERFORMANCE_VOLUME,
    pressureCurve: 'linear',
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
    midiOutputs: [],
    selectedMidiId: '',
    selectedMidiOutputId: '',
    midiStatus: 'MIDI is off.',
    exquisSyncEnabled: false,
    exquisSyncStatus: 'Exquis sync: off',
    exquisSysexAvailable: false,
    exquisProtocol: 'auto',
    exquisDialListenEnabled: false,
    exquisDeveloperMask: 0,
    activeEdgeControlId: '',
    lastEdgeControlId: '',
    lastEdgeControlValue: '',
    legacyMap: 'bottom_left',
    legacyLightTarget: 'buttons',
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
    pendingLogs.push(stamp + ' [' + kind + '] ' + message);
    scheduleLogFlush();
  }

  function scheduleLogFlush() {
    if (logFlushTimer) return;
    logFlushTimer = window.setTimeout(flushLogs, 32);
  }

  function flushLogs() {
    logFlushTimer = null;
    if (!pendingLogs.length) return;
    Array.prototype.push.apply(logs, pendingLogs);
    pendingLogs = [];
    if (logs.length > 120) logs.shift();
    if (logs.length > 120) logs = logs.slice(logs.length - 120);
    if (els.diagnosticLog) {
      els.diagnosticLog.textContent = logs.join('\n') || 'Ready.';
      els.diagnosticLog.scrollTop = els.diagnosticLog.scrollHeight;
    }
  }

  function allLogText() {
    return logs.concat(pendingLogs).join('\n') || 'Ready.';
  }

  window.__exquisDebugLog = logEvent;

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

  function objectKeyCount(obj) {
    return Object.keys(obj || {}).length;
  }

  function getSsliActiveOscillators() {
    var host = getSsliHost();
    if (!host || !host.SynthLab || !host.SynthLab.audio || !host.SynthLab.audio.getActiveOscillators) return null;
    return host.SynthLab.audio.getActiveOscillators();
  }

  function getSsliActiveOscillatorCount() {
    var activeOscs = getSsliActiveOscillators();
    return activeOscs && typeof activeOscs.size === 'number' ? activeOscs.size : null;
  }

  function currentScopePeak() {
    if (!audioAnalyser || !audioScopeData || !audioAnalyser.getByteTimeDomainData) return null;
    audioAnalyser.getByteTimeDomainData(audioScopeData);
    var peak = 0;
    for (var i = 0; i < audioScopeData.length; i++) {
      peak = Math.max(peak, Math.abs((audioScopeData[i] - 128) / 128));
    }
    return peak;
  }

  function logSsliAudioHealth(reason) {
    var host = getSsliHost();
    var SL = host && host.SynthLab;
    var audio = SL && SL.audio;
    var ctx = audio && audio.getCtx ? audio.getCtx() : null;
    var activeOscs = audio && audio.getActiveOscillators ? audio.getActiveOscillators() : null;
    var pool = audio && audio.getVoicePoolStats ? audio.getVoicePoolStats() : null;
    var inst = audio && audio.getCurrentInstrument ? audio.getCurrentInstrument() : null;
    var type = audio && audio.getInstrumentType && inst !== null ? audio.getInstrumentType(inst) : 'n/a';
    var scopePeak = currentScopePeak();
    var parts = [
      'SSLI health ' + reason,
      'ctx=' + (ctx ? ctx.state : 'n/a'),
      't=' + (ctx && typeof ctx.currentTime === 'number' ? ctx.currentTime.toFixed(3) : 'n/a'),
      'lat=' + (ctx && typeof ctx.baseLatency === 'number' ? ctx.baseLatency.toFixed(3) : 'n/a'),
      'inst=' + (inst === null ? 'n/a' : inst),
      'type=' + type,
      'held=' + objectKeyCount(state.heldNotes),
      'local=' + objectKeyCount(midiVoices),
      'activeOsc=' + (activeOscs && typeof activeOscs.size === 'number' ? activeOscs.size : 'n/a'),
      'nodeCount=' + (audio && typeof audio._activeNodeCount === 'number' ? audio._activeNodeCount : 'n/a'),
      'scopePeak=' + (scopePeak === null ? 'n/a' : Math.round(scopePeak * 100) + '%')
    ];
    if (pool) {
      parts.push(
        'poolActive=' + (typeof pool.currentlyActive === 'number' ? pool.currentlyActive : 'n/a'),
        'poolAvail=' + (typeof pool.available === 'number' ? pool.available : 'n/a'),
        'poolPeak=' + (typeof pool.peakUsage === 'number' ? pool.peakUsage : 'n/a'),
        'steals=' + (typeof pool.steals === 'number' ? pool.steals : 'n/a'),
        'poolTotal=' + (typeof pool.totalAllocated === 'number' ? pool.totalAllocated : 'n/a')
      );
    } else {
      parts.push('poolActive=n/a', 'poolAvail=n/a', 'poolPeak=n/a', 'steals=n/a', 'poolTotal=n/a');
    }
    logEvent('audio', parts.join(' '));
    if (type !== 'physical' && pool && activeOscs && typeof activeOscs.size === 'number' && typeof pool.currentlyActive === 'number' && activeOscs.size !== pool.currentlyActive) {
      logEvent('audio', 'SSLI health warning activeOsc/pool mismatch activeOsc=' + activeOscs.size + ' poolActive=' + pool.currentlyActive);
    }
  }

  function localSsliVoiceMidiSet() {
    var midis = {};
    Object.keys(midiVoices).forEach(function(key) {
      var voice = midiVoices[key];
      if (voice && voice.ssli) midis[voice.midi] = true;
    });
    return midis;
  }

  function logMidiVoiceStats(reason) {
    var ssliCount = getSsliActiveOscillatorCount();
    logEvent('audio', 'MIDI voices ' + reason + ' held=' + objectKeyCount(state.heldNotes) + ' local=' + objectKeyCount(midiVoices) + ' ssli=' + (ssliCount === null ? 'n/a' : ssliCount));
  }

  function getExquisDebugSnapshot() {
    return {
      heldNotes: objectKeyCount(state.heldNotes),
      midiVoices: objectKeyCount(midiVoices),
      ssliActiveOscillators: getSsliActiveOscillatorCount(),
      lastAppliedSsliPresetKey: lastAppliedSsliPresetKey,
      soundPresetId: state.soundPresetId,
      mode: state.mode,
      exerciseId: state.exerciseId,
      currentPath: currentPath.map(function(cell, index) {
        return {
          index: index,
          id: cell.id,
          cellId: cell.id.replace('-octave', ''),
          midi: cell.midi,
          label: noteLabelFromMidi(cell.midi),
          virtual: !!cell.virtual
        };
      })
    };
  }

  window.__exquisDebugSnapshot = getExquisDebugSnapshot;

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

  var EXQUIS_SYSEX_HEADER = [0xF0, 0x00, 0x21, 0x7E, 0x7F];
  var EXQUIS_DEVELOPER_PADS_MASK = 0x01;
  var EXQUIS_DEVELOPER_ENCODERS_MASK = 0x02;
  var EXQUIS_DEVELOPER_SETTINGS_SOUND_MASK = 0x10;
  var EXQUIS_DEVELOPER_DIAL_LISTEN_MASK = EXQUIS_DEVELOPER_PADS_MASK | EXQUIS_DEVELOPER_ENCODERS_MASK | EXQUIS_DEVELOPER_SETTINGS_SOUND_MASK;
  var EXQUIS_DEVELOPER_LEGACY_PROBE_MASK = 0x20;

  function clamp7Bit(value) {
    return Math.max(0, Math.min(127, Math.round(Number(value) || 0)));
  }

  function buildExquisSysex(command, payload) {
    var bytes = EXQUIS_SYSEX_HEADER.slice();
    bytes.push(clamp7Bit(command));
    payload = payload || [];
    for (var i = 0; i < payload.length; i++) bytes.push(clamp7Bit(payload[i]));
    bytes.push(0xF7);
    return bytes;
  }

  function buildExquisLegacySysex(command, payload) {
    var bytes = [0xF0, 0x00, 0x21, 0x7E];
    if (typeof command === 'number') bytes.push(clamp7Bit(command));
    payload = payload || [];
    for (var i = 0; i < payload.length; i++) bytes.push(clamp7Bit(payload[i]));
    bytes.push(0xF7);
    return bytes;
  }

  function bytesToHex(bytes) {
    return Array.prototype.slice.call(bytes || []).map(function(byte) {
      return byte.toString(16).padStart(2, '0').toUpperCase();
    }).join(' ');
  }

  function parseExquisSysex(data) {
    var bytes = Array.prototype.slice.call(data || []);
    if (bytes.length < 7) return null;
    for (var i = 0; i < EXQUIS_SYSEX_HEADER.length; i++) {
      if (bytes[i] !== EXQUIS_SYSEX_HEADER[i]) return null;
    }
    if (bytes[bytes.length - 1] !== 0xF7) return null;
    return {
      command: bytes[5],
      payload: bytes.slice(6, -1),
      bytes: bytes
    };
  }

  function scaleDegreesFor(scaleId) {
    var key = scaleId || state.scaleId;
    var scaleData = SSLI_MODES[key] || SSLI_MODES.ionian || {};
    var intervals = scaleData.scale || [0, 2, 4, 5, 7, 9, 11];
    var degrees = [];
    for (var pc = 0; pc < 12; pc++) degrees.push(intervals.indexOf(pc) >= 0 ? 1 : 0);
    return degrees;
  }

  function scaleIndexFor(scaleId) {
    var index = SCALE_KEYS.indexOf(scaleId);
    return index >= 0 ? index : 0;
  }

  function scaleIdForIndex(index) {
    index = clamp7Bit(index);
    return SCALE_KEYS[index] || '';
  }

  function exquisScaleNumberForScaleId(scaleId) {
    if (Object.prototype.hasOwnProperty.call(EXQUIS_SCALE_NUMBER_BY_ID, scaleId)) return EXQUIS_SCALE_NUMBER_BY_ID[scaleId];
    return 0;
  }

  function scaleIdForExquisNumber(scaleNumber) {
    scaleNumber = clamp7Bit(scaleNumber);
    return EXQUIS_SCALE_ID_BY_NUMBER[scaleNumber] || '';
  }

  function updateTonicFromHardwareRoot(rootPc, source) {
    var incomingPc = mod(rootPc, 12);
    exquisSyncSuppressUntil = Date.now() + 250;
    if (incomingPc !== state.tonicPc) {
      state.tonicPc = incomingPc;
      state.rootCellId = '';
      state.step = 0;
    }
    state.exquisSyncStatus = 'Exquis sync: received root ' + getTonicName() + ' from ' + source;
    render();
  }

  function updateScaleFromHardwareNumber(scaleNumber, source) {
    var scaleId = scaleIdForExquisNumber(scaleNumber);
    exquisSyncSuppressUntil = Date.now() + 250;
    if (scaleId) {
      if (scaleId !== state.scaleId) {
        state.scaleId = scaleId;
        state.step = 0;
      }
      state.exquisSyncStatus = 'Exquis sync: received scale ' + getScale().name + ' from ' + source + ' number=' + scaleNumber;
    } else {
      state.exquisSyncStatus = 'Exquis sync: received hardware scale number ' + scaleNumber + ' from ' + source + ' (unmapped)';
    }
    render();
  }

  window.__exquisSysexDebug = {
    build: buildExquisSysex,
    parse: parseExquisSysex,
    degreesFor: scaleDegreesFor,
    scaleIndexFor: scaleIndexFor,
    scaleIdForIndex: scaleIdForIndex,
    exquisScaleNumberFor: exquisScaleNumberForScaleId,
    scaleIdForExquisNumber: scaleIdForExquisNumber,
    developerMask: EXQUIS_DEVELOPER_PADS_MASK,
    legacy: buildExquisLegacySysex
  };

  function getStrategy() {
    for (var i = 0; i < STRATEGIES.length; i++) {
      if (STRATEGIES[i].id === state.strategyId) return STRATEGIES[i];
    }
    return STRATEGIES[0];
  }

  function getExercise() {
    for (var i = 0; i < EXERCISES.length; i++) {
      if (EXERCISES[i].id === state.exerciseId) return EXERCISES[i];
    }
    return EXERCISES[0];
  }

  function exerciseButtonLabel(exercise) {
    if (exercise.id === 'root_octave') return '1 Oct';
    if (exercise.id === 'two_octaves') return '2 Oct';
    if (exercise.id === 'inner_ladder') return 'Chain';
    if (exercise.id === 'root_returns') return 'Root';
    return exercise.name;
  }

  function getStrategyFingers(strategy) {
    return state.hand === 'right' ? strategy.rightFingers : strategy.leftFingers;
  }

  function fingerName(finger) {
    var names = {
      1: 'Thumb',
      2: 'Index',
      3: 'Middle',
      4: 'Ring',
      5: 'Pinky'
    };
    return names[finger] || 'Finger ' + String(finger);
  }

  function fingerShortName(finger) {
    var names = {
      1: 'Th',
      2: 'In',
      3: 'Mid',
      4: 'Ring',
      5: 'Pink'
    };
    return names[finger] || 'F' + String(finger);
  }

  function fingerDisplayName(finger) {
    return fingerName(finger) + ' (' + String(finger) + ')';
  }

  function getHandRule(strategy) {
    if (state.hand === 'right') {
      return strategy.rule.replace('5-4-3-2', '2-3-4-5').replace('4-3-2-1', '1-2-3-4');
    }
    return strategy.rule;
  }

  function describeButtonChoice(cells, current, root) {
    if (!current) return 'No target selected.';
    var exactMatches = [];
    var chainMatches = [];
    for (var i = 0; i < cells.length; i++) {
      if (cells[i].midi !== current.midi) continue;
      exactMatches.push(cells[i]);
      if (!root || isInnerChainCell(cells[i], root)) chainMatches.push(cells[i]);
    }
    var note = noteName(current.midi) + octave(current.midi);
    if (exactMatches.length > 1) {
      return 'Exact ' + note + '; duplicates -> two-chain, then center.';
    }
    return 'Exact ' + note + '; on the two-chain path.';
  }

  function describeFingerChoice(strategy, stepIndex, finger, fingers) {
    var hand = state.hand === 'right' ? 'right' : 'left';
    var groupSize = strategy.id === 'ladder4' || strategy.id === 'position_shift' || strategy.id === 'wrist_pairs' || strategy.id === 'natural_clusters' ? 4 : Math.max(1, fingers.length);
    var groupPosition = mod(stepIndex, groupSize) + 1;
    var groupNumber = Math.floor(stepIndex / groupSize) + 1;
    if (strategy.id === 'ladder4') {
      return fingerDisplayName(finger) + ' = ' + hand + ' group ' + groupNumber + ', step ' + groupPosition + '; shape scaffold, not piano law.';
    }
    if (strategy.id === 'position_shift') {
      return fingerDisplayName(finger) + ' inside a compact position; move the whole hand between groups.';
    }
    if (strategy.id === 'wrist_pairs') {
      return fingerDisplayName(finger) + ' may cover a pair; the wrist moves the hand, not a finger stretch.';
    }
    if (strategy.id === 'natural_clusters') {
      return fingerDisplayName(finger) + ' follows the hand cluster: pinky start, paired middle area, index-led top.';
    }
    return fingerDisplayName(finger) + ' supports the turn; avoid default piano thumb-under.';
  }

  function describeMotionChoice(strategy, stepIndex, fingers) {
    var groupSize = strategy.id === 'ladder4' || strategy.id === 'position_shift' || strategy.id === 'wrist_pairs' || strategy.id === 'natural_clusters' ? 4 : Math.max(1, fingers.length);
    var groupPosition = mod(stepIndex, groupSize) + 1;
    if (strategy.id === 'position_shift') {
      return groupPosition === 1 && stepIndex > 0 ? 'Shift wrist/hand to a fresh compact position.' : 'Stay inside the current compact position.';
    }
    if (strategy.id === 'wrist_pairs') {
      return groupPosition === 2 || groupPosition === 3 ? 'Let the wrist carry this pair; keep pressure vertical.' : 'Reset hand shape before the next pair.';
    }
    if (strategy.id === 'natural_clusters') {
      return groupPosition === 1 ? 'Anchor the hand shape gently; no reaching.' : 'Let the hand roll through the cluster with vertical pressure.';
    }
    if (strategy.id === 'ladder4') {
      return groupPosition === 1 && stepIndex > 0 ? 'Move wrist/hand; repeat the Exquis shape.' : 'Relax wrist; finger change is not a stretch command.';
    }
    return groupPosition >= groupSize - 1 ? 'Use thumb as assist, then release tension.' : 'Stay shape-centered; let the hand float.';
  }

  function isHandShiftStep(strategy, stepIndex) {
    if (stepIndex <= 0) return false;
    if (strategy.id !== 'ladder4' && strategy.id !== 'position_shift' && strategy.id !== 'wrist_pairs' && strategy.id !== 'natural_clusters') return false;
    return mod(stepIndex, 4) === 0;
  }

  function distanceBetweenCells(a, b) {
    if (!a || !b) return 0;
    var dx = a.x - b.x;
    var dy = a.y - b.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  function fittsMovementCost(distance, targetWidth) {
    var width = Math.max(1, targetWidth || CELL_W);
    return Math.log(distance / width + 1) / Math.log(2);
  }

  function fingerWeaknessCost(finger) {
    if (finger === 4) return 0.8;
    if (finger === 5) return 0.7;
    if (finger === 3) return 0.35;
    if (finger === 1) return 0.25;
    return 0.1;
  }

  function repeatedFingerCost(previousFinger, currentFinger, distance) {
    if (!previousFinger || previousFinger !== currentFinger) return 0;
    if (distance < CELL_W * 0.8) return 0.4;
    if (distance < CELL_W * 1.8) return 1.1;
    return 2.2;
  }

  function scoreErgonomicStep(path, fingers, strategy, stepIndex) {
    var current = path[stepIndex] || null;
    if (!current) return { score: 0, level: 'unscored', text: 'Movement load: no target.' };
    var previousIndex = stepIndex > 0 ? stepIndex - 1 : -1;
    var previous = previousIndex >= 0 ? path[previousIndex] : null;
    var currentFinger = fingers[mod(stepIndex, fingers.length)];
    var previousFinger = previous ? fingers[mod(previousIndex, fingers.length)] : 0;
    var distance = previous ? distanceBetweenCells(previous, current) : 0;
    var travel = previous ? fittsMovementCost(distance, CELL_W) : 0;
    var repeated = repeatedFingerCost(previousFinger, currentFinger, distance);
    var weak = fingerWeaknessCost(currentFinger);
    var shift = isHandShiftStep(strategy, stepIndex) ? 0.9 : 0;
    var pressure = (currentFinger === 4 || currentFinger === 5 ? 0.55 : 0.2);
    var score = travel + repeated + weak + shift + pressure;
    var level = score < 2.0 ? 'low' : (score < 3.6 ? 'medium' : 'high');
    var reasons = [];
    if (previous) reasons.push('travel ' + String(Math.round(distance)) + 'px');
    if (repeated) reasons.push('same ' + fingerName(currentFinger).toLowerCase());
    if (shift) reasons.push('hand shift');
    if (weak > 0.6) reasons.push(fingerName(currentFinger).toLowerCase() + ' pressure risk');
    if (!reasons.length) reasons.push('anchor');
    return {
      score: score,
      level: level,
      text: 'Movement load: ' + level + ' (' + reasons.join(', ') + ').'
    };
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

  function soundEngineKey(engine) {
    return String(engine || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  function isMatureSoundEngine(engine) {
    return !!MATURE_SOUND_ENGINES[soundEngineKey(engine)];
  }

  function getVisibleSoundEngines() {
    var engines = getSoundEngines();
    if (state.showAllEngines) return engines;
    var mature = engines.filter(isMatureSoundEngine);
    return mature.length ? mature : engines;
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

  function ensureFreshSsliFrame() {
    var frame = document.getElementById('ssliEngineFrame');
    if (!frame) return;
    var freshSrc = 'ssli/index.html?v={{BUILD_TIMESTAMP_UTC}}';
    if (frame.getAttribute('src') !== freshSrc) frame.setAttribute('src', freshSrc);
    if (!navigator.serviceWorker || !navigator.serviceWorker.getRegistrations) return;
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
      var removed = false;
      registrations.forEach(function(registration) {
        var scope = registration && registration.scope ? registration.scope : '';
        if (scope.indexOf('/ssli/') >= 0 || scope.indexOf('/dist/ssli/') >= 0) {
          removed = true;
          registration.unregister();
        }
      });
      if (removed) {
        logEvent('audio', 'removed stale SSLI service worker cache; reloading runtime frame');
        frame.setAttribute('src', freshSrc + '&reload=' + Date.now());
      }
    }).catch(function(err) {
      logEvent('audio', 'SSLI service worker cleanup warning: ' + (err && err.message ? err.message : err));
    });
  }

  function describeSsliReadiness(SL, mode) {
    if (!SL) return 'missing SynthLab host';
    if (!SL.audio) return 'missing SynthLab.audio';
    if (!SL.presets) return 'missing SynthLab.presets';
    if (!SL.presets.apply) return 'missing SynthLab.presets.apply';
    if (mode === 'midi') {
      if (!SL.audio.getInstruments) return 'missing SynthLab.audio.getInstruments';
      if (!SL.audio.getCurrentInstrument) return 'missing SynthLab.audio.getCurrentInstrument';
      if (!SL.audio.startSustainedNote) return 'missing SynthLab.audio.startSustainedNote';
    }
    return 'ready';
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
    if (payload && payload.engine === 'physical' && payload.settings) {
      var physical = payload.settings.physicalSettings || {};
      ['model', 'damping', 'brightness', 'excitation', 'bodySize', 'pickPosition', 'decayTime', 'bowPressure', 'bowPosition', 'breathPressure', 'embouchure', 'strikePosition', 'hardness', 'material'].forEach(function(key) {
        if (payload.settings[key] != null && physical[key] == null) physical[key] = payload.settings[key];
      });
      payload.settings.physicalSettings = physical;
    }
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
    applyExhibitPresetCorrections(payload);
    normalizeSsliPresetPayload(payload, SL);
    return payload;
  }

  function applyExhibitPresetCorrections(payload) {
    if (!payload || !payload.engine || !payload.name) return payload;
    var corrected = getCorrectedFallbackPreset(payload.engine, payload.name);
    if (!corrected || !corrected.settings) return payload;
    payload.settings = clonePreset(corrected.settings);
    logEvent('audio', 'SSLI preset corrected engine=' + payload.engine + ' preset=' + payload.name);
    return payload;
  }

  function getCorrectedFallbackPreset(engine, presetName) {
    var library = SSLI_PRESETS[engine] || {};
    var presets = library.presets || [];
    var correctionName = presetName;
    if (engine === 'subtractive') {
      var subtractiveNameMap = {
        'Synth Brass Section': 'Brass Section',
        'Synth Brass Section II': 'Brass Section II'
      };
      correctionName = subtractiveNameMap[presetName] || presetName;
    }
    for (var i = 0; i < presets.length; i++) {
      if (presets[i] && presets[i].name === correctionName && (presets[i].exhibitTimbreCorrection || engine === 'physical')) {
        return presets[i];
      }
    }
    return null;
  }

  function applySelectedSsliPreset() {
    var host = getSsliHost();
    if (!host) {
      logEvent('audio', 'SSLI preset apply failed: missing runtime host for ' + state.soundPresetId);
      scheduleSsliPresetApplyRetry('missing runtime host');
      return false;
    }
    var SL = host.SynthLab;
    var presetKey = currentSsliPresetKey();
    var preset = getSsliPresetPayload(SL);
    if (lastAppliedSsliPresetKey === presetKey && objectKeyCount(midiVoices) > 0 && hasSsliInstrumentOutput(SL)) {
      return true;
    }
    if (lastAppliedSsliPresetKey === presetKey && preset && hasSsliInstrumentOutput(SL) && verifySsliPresetRuntime(SL, preset, false)) return true;
    var readiness = describeSsliReadiness(SL, 'apply');
    if (!preset || readiness !== 'ready') {
      logEvent('audio', 'SSLI preset apply failed: ' + (!preset ? 'missing selected runtime preset' : readiness) + ' preset=' + state.soundPresetId);
      scheduleSsliPresetApplyRetry(!preset ? 'missing selected runtime preset' : readiness);
      return false;
    }
    ensureSsliAudioReady(SL);
    if (SL.audio.stopAllSustained) SL.audio.stopAllSustained();
    cleanupSsliEngineVoices(SL, 'before preset apply');
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
    verifySsliPresetRuntime(SL, preset, true);
    return true;
  }

  function hasSsliInstrumentOutput(SL) {
    if (!SL || !SL.audio || !SL.audio.getInstruments) return false;
    var inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    var instruments = SL.audio.getInstruments() || [];
    return Boolean(instruments[inst] && instruments[inst].masterOutput);
  }

  function scheduleSsliPresetApplyRetry(reason) {
    if (ssliPresetRetryTimer) return;
    var attempts = 0;
    ssliPresetRetryTimer = window.setInterval(function() {
      attempts += 1;
      var host = getSsliHost();
      if (host && host.SynthLab && describeSsliReadiness(host.SynthLab, 'apply') === 'ready') {
        window.clearInterval(ssliPresetRetryTimer);
        ssliPresetRetryTimer = null;
        logEvent('audio', 'SSLI runtime became ready; retrying preset apply after ' + reason);
        applySelectedSsliPreset();
      } else if (attempts >= 30) {
        window.clearInterval(ssliPresetRetryTimer);
        ssliPresetRetryTimer = null;
        logEvent('audio', 'SSLI preset retry gave up after ' + reason);
      }
    }, 250);
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

  function callSsliAllNotesOff(SL, engineName, inst) {
    if (!SL || !SL[engineName] || !SL[engineName].allNotesOff) return false;
    try {
      SL[engineName].allNotesOff(inst);
      return true;
    } catch (err) {
      logEvent('audio', 'SSLI ' + engineName + ' all-notes-off warning: ' + (err && err.message ? err.message : err));
      return false;
    }
  }

  function cleanupSsliEngineVoices(SL, reason) {
    if (!SL || !SL.audio) return false;
    var inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    var cleaned = false;
    [
      'fm', 'physical', 'additive', 'granular', 'vocoderSynth',
      'wavefolder', 'formant', 'modal', 'ringmod', 'chord',
      'superwave', 'wavetableSynth', 'phasedist', 'chip',
      'bytebeat', 'vector', 'drumsyn', 'pulsar', 'bodyResonance', 'reed'
    ].forEach(function(engineName) {
      cleaned = callSsliAllNotesOff(SL, engineName, inst) || cleaned;
    });
    if (cleaned && reason) logEvent('audio', 'SSLI engine all-notes-off ' + reason + ' inst=' + inst);
    return cleaned;
  }

  function getCurrentPhysicalModel(SL) {
    var current = getSsliInstrument(SL);
    var instrument = current && current.instrument;
    var settings = instrument && instrument.settings;
    var physical = settings && settings.physicalSettings;
    return physical && physical.model ? physical.model : '';
  }

  function hashObject(value) {
    var text = '';
    try {
      text = JSON.stringify(value || {});
    } catch (err) {
      text = String(value || '');
    }
    var hash = 0;
    for (var i = 0; i < text.length; i++) {
      hash = ((hash << 5) - hash + text.charCodeAt(i)) | 0;
    }
    return String(hash);
  }

  function getEngineSettingsForInstrument(instrument) {
    var settings = instrument && instrument.settings ? instrument.settings : {};
    var type = instrument && instrument.type ? instrument.type : '';
    var keyByType = {
      fm: 'fmSettings',
      physical: 'physicalSettings',
      wavetable: 'wavetableSettings',
      additive: 'additiveSettings',
      granular: 'granularSettings',
      modal: 'modalSettings',
      ringmod: 'ringmodSettings',
      superwave: 'superwaveSettings',
      wavefolder: 'wavefoldSettings',
      formant: 'formantSettings',
      chord: 'chordSettings',
      phasedist: 'phasedistSettings',
      chip: 'chipSettings',
      vector: 'vectorSettings',
      drumsyn: 'drumsynSettings',
      pulsar: 'pulsarSettings',
      reed: 'reedSettings'
    };
    var key = keyByType[type] || '';
    return {
      key: key,
      value: key ? (settings[key] || {}) : { osc: settings.osc || null, filter: settings.filter || null, adsr: settings.adsr || null }
    };
  }

  function verifySsliPresetRuntime(SL, preset, shouldLog) {
    var current = getSsliInstrument(SL);
    if (!current || !current.instrument || !preset) return false;
    var instrument = current.instrument;
    var expected = preset.engine || '';
    var actual = instrument.type || '';
    var engineSettings = getEngineSettingsForInstrument(instrument);
    var settingsHash = hashObject(instrument.settings || {});
    var engineSettingsHash = hashObject(engineSettings.value);
    var ok = !expected || actual === expected;
    if (shouldLog || !ok) {
      logEvent('audio', 'SSLI runtime inst=' + current.id + ' type=' + actual + ' expected=' + expected + ' settings=' + settingsHash + ' engineSettings=' + engineSettingsHash + (ok ? '' : ' MISMATCH'));
    }
    return ok;
  }

  function shouldUseFastMidiPath(SL) {
    return lastAppliedSsliPresetKey === currentSsliPresetKey() && objectKeyCount(midiVoices) > 0 && !state.filterDirty && !state.fxDirty && !!SL;
  }

  function ensureSsliPracticeVolume(SL, inst, targetVolume) {
    if (!SL || !SL.audio || !SL.audio.getInstruments) return;
    var instruments = SL.audio.getInstruments() || [];
    var instrument = instruments[inst] || {};
    var settings = instrument.settings || {};
    var currentVolume = typeof settings.volume === 'number' ? settings.volume : null;
    targetVolume = typeof targetVolume === 'number' ? targetVolume : 100;
    if (SL.audio.setInstrumentVolume && (currentVolume === null || Math.abs(currentVolume - targetVolume) >= 1)) {
      SL.audio.setInstrumentVolume(inst, targetVolume);
      logEvent('audio', 'SSLI instrument inst=' + inst + ' type=' + (instrument.type || 'unknown') + ' volume=' + (currentVolume === null ? 'unset' : currentVolume) + '->' + targetVolume);
    } else {
      logEvent('audio', 'SSLI instrument inst=' + inst + ' type=' + (instrument.type || 'unknown') + ' volume=' + (currentVolume === null ? 'unset' : currentVolume));
    }
  }

  function ensureSsliAudioReady(SL) {
    if (!SL || !SL.audio) return;
    if (SL.audio.getCtx) SL.audio.getCtx();
    if (SL.audio.initEffectChain && !hasSsliInstrumentOutput(SL)) SL.audio.initEffectChain();
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
    var raw = Math.max(1, Math.min(127, Math.round(velocity || 1)));
    var level = raw / 127;
    if (state.pressureCurve === 'soft') {
      level = Math.sqrt(level);
    } else if (state.pressureCurve === 'hard') {
      level = level * level;
    }
    // Source: MIDI 1.0 Detailed Specification, Channel Voice Message
    // note-on velocity is transmitted as a 7-bit velocity value. Keep the
    // default linear curve linear; only the explicit UI pressure curves remap it.
    return Math.max(1, Math.min(127, Math.round(level * 127)));
  }

  function playableFmMidiVelocity(velocity) {
    var raw = Math.max(1, Math.min(127, Math.round(velocity || 1)));
    var level = raw / 127;
    // Source: MIDI 1.0 Detailed Specification, Channel Voice Message defines
    // note-on velocity as 7-bit key-strike velocity; Dexed/msfa dx7note.cc
    // ScaleVelocity() then applies that MIDI velocity through each operator's
    // velocity sensitivity. Exquis pressure is controller pressure, so translate
    // it to a playable note-on velocity before the unmodified DX7 patch math.
    return Math.max(1, Math.min(127, Math.round(Math.sqrt(level) * 127)));
  }

  function currentSsliNormalization() {
    if (SSLI_PRESET_NORMALIZATION[state.soundPresetId]) return SSLI_PRESET_NORMALIZATION[state.soundPresetId];
    if (MATURE_SOUND_ENGINES[soundEngineKey(state.soundEngine)]) return SSLI_MATURE_ENGINE_NORMALIZATION;
    return null;
  }

  function normalizedSsliInstrumentVolume(normalization) {
    var base = Math.max(0, Math.min(100, Number(state.performanceVolume || DEFAULT_PERFORMANCE_VOLUME)));
    if (!normalization || typeof normalization.instrumentVolume !== 'number') return base;
    return Math.max(0, Math.min(100, Math.round(base * normalization.instrumentVolume / SSLI_NORMALIZATION_BASE_VOLUME)));
  }

  function normalizedSsliOutputGain(normalization) {
    if (!normalization || typeof normalization.outputGain !== 'number') return 1;
    return Math.max(0.1, Math.min(SSLI_NORMALIZATION_MAX_OUTPUT_GAIN, normalization.outputGain));
  }

  function ensureSsliOutputNormalization(SL, inst, normalization) {
    if (!SL || !SL.audio || !SL.audio.getInstruments) return;
    var instruments = SL.audio.getInstruments() || [];
    var instrument = instruments[inst] || {};
    var outputGain = normalizedSsliOutputGain(normalization);
    if (instrument.masterOutput && instrument.masterOutput.gain && typeof instrument.masterOutput.gain.value === 'number') {
      var current = instrument.masterOutput.gain.value;
      if (Math.abs(current - outputGain) >= 0.01) {
        var ctx = SL.audio.getCtx ? SL.audio.getCtx() : null;
        var param = instrument.masterOutput.gain;
        var now = ctx && typeof ctx.currentTime === 'number' ? ctx.currentTime : 0;
        // Web Audio AudioParam automation prevents gain discontinuities that
        // sound like clicks/pops when normalization changes at note start.
        // Original source: W3C Web Audio API, AudioParam setTargetAtTime().
        if (param.cancelScheduledValues && param.setValueAtTime && param.setTargetAtTime) {
          param.cancelScheduledValues(now);
          param.setValueAtTime(Math.max(0.0001, current || 0.0001), now);
          param.setTargetAtTime(outputGain, now, 0.012);
        } else {
          param.value = outputGain;
        }
        logEvent('audio', 'SSLI normalization output preset=' + state.soundPresetId + ' gain=' + outputGain.toFixed(2));
      }
    } else if (normalization && normalization.outputGain) {
      logEvent('audio', 'SSLI normalization output unavailable preset=' + state.soundPresetId + ' gain=' + outputGain.toFixed(2));
    }
  }

  function ensureSsliPerformanceGain(SL, inst) {
    var normalization = currentSsliNormalization();
    var targetVolume = normalizedSsliInstrumentVolume(normalization);
    ensureSsliPracticeVolume(SL, inst, targetVolume);
    ensureSsliOutputNormalization(SL, inst, normalization);
    if (normalization) {
      logEvent('audio', 'SSLI normalization preset=' + state.soundPresetId + ' volume=' + targetVolume + ' output=' + normalizedSsliOutputGain(normalization).toFixed(2));
    }
  }

  function heldSsliVoiceCount() {
    var count = 0;
    Object.keys(midiVoices).forEach(function(key) {
      if (midiVoices[key] && midiVoices[key].ssli && !midiVoices[key].oneShot) count += 1;
    });
    return count;
  }

  function activeSsliOneShotCount() {
    var count = 0;
    Object.keys(midiVoices).forEach(function(key) {
      var voice = midiVoices[key];
      if (voice && voice.ssli && voice.oneShot) count += 1;
    });
    return count;
  }

  function effectiveHeldPhysicalVoicesForVelocity(heldPhysicalVoices) {
    var held = Math.max(0, Math.round(heldPhysicalVoices || 0));
    if (held <= 0) return 0;
    var nowMs = Date.now();
    var recentPhysicalVoices = 0;
    Object.keys(midiVoices).forEach(function(key) {
      var voice = midiVoices[key];
      if (!voice || !voice.ssli || voice.instrumentType !== 'physical') return;
      if (nowMs - (voice.startedAt || 0) <= PHYSICAL_SIMULTANEOUS_ONSET_MS) recentPhysicalVoices += 1;
    });
    if (recentPhysicalVoices === held && held < PHYSICAL_UNSCALED_SIMULTANEOUS_VOICES) return 0;
    return held;
  }

  function playablePhysicalMidiVelocity(velocity, heldPhysicalVoices) {
    var raw = Math.max(1, Math.min(127, Math.round(velocity || 1)));
    var held = Math.max(0, Math.min(6, Math.round(heldPhysicalVoices || 0)));
    var scales = [1, 0.72, 0.56, 0.42, 0.3, 0.22, 0.18];
    var voiceLoadScale = scales[held] || 0.18;
    var cap = Math.max(42, Math.round(96 * voiceLoadScale));
    var floor = Math.max(32, Math.round(48 * voiceLoadScale));
    return Math.max(floor, Math.min(cap, Math.round(raw * 1.5 * voiceLoadScale)));
  }

  function immediateArticulation() {
    return {
      family: 'sustained',
      onsetMode: 'immediate',
      captureWindowMs: 0,
      minInterOnsetMs: 0,
      maxSpreadMs: 0,
      order: 'input',
      pressurePolicy: 'live'
    };
  }

  function defaultArticulationForPreset(engine, preset) {
    var engineKey = soundEngineKey(engine || (preset && preset.engine));
    var category = String((preset && preset.category) || '').toLowerCase();
    var settings = (preset && preset.settings) || {};
    var physical = settings.physicalSettings || {};
    var physicalModel = String(settings.model || physical.model || '').toLowerCase();
    if (engineKey === 'physical' && (category === 'plucked' || physicalModel === 'pluck')) {
      return {
        family: 'plucked',
        onsetMode: 'strum',
        captureWindowMs: 18,
        minInterOnsetMs: 11,
        maxSpreadMs: 46,
        order: 'physical-low-to-high',
        pressurePolicy: 'onset-only',
        autoDampMs: SSLI_PHYSICAL_PLUCK_AUTO_DAMP_MS
      };
    }
    if (engineKey === 'physical' && physicalModel === 'strike') {
      return {
        family: 'struck',
        onsetMode: 'roll',
        captureWindowMs: 10,
        minInterOnsetMs: 5,
        maxSpreadMs: 18,
        order: 'physical-low-to-high',
        pressurePolicy: 'capture-and-apply-at-onset'
      };
    }
    return immediateArticulation();
  }

  function selectedArticulation() {
    var option = getCurrentSoundPreset();
    var preset = option && option.preset;
    var articulation = preset && preset.articulation;
    return articulation || defaultArticulationForPreset(option && option.family, preset);
  }

  function selectedArticulationMode() {
    return selectedArticulation().onsetMode || 'immediate';
  }

  function physicalOrderValue(event) {
    var cells = makeGrid();
    var cell = event.cellId ? cells.find(function(candidate) { return candidate.id === event.cellId; }) : null;
    if (!cell) cell = findCellByMidi(cells, event.midi);
    if (!cell) return event.midi * 1000 + event.sequence;
    return cell.row * 100 + cell.col;
  }

  function removePendingArticulation(key) {
    var removed = false;
    articulationQueue = articulationQueue.filter(function(event) {
      if (event.key === key) {
        if (event.timer) window.clearTimeout(event.timer);
        removed = true;
        return false;
      }
      return true;
    });
    if (!articulationQueue.length && articulationFlushTimer) {
      window.clearTimeout(articulationFlushTimer);
      articulationFlushTimer = null;
    }
    return removed;
  }

  function releasePendingArticulation(key) {
    var removed = false;
    var nowMs = Date.now();
    articulationQueue = articulationQueue.filter(function(event) {
      if (event.key !== key) return true;
      var articulation = event.articulation || {};
      var captureWindow = Math.max(0, Number(articulation.captureWindowMs || 0));
      var elapsed = nowMs - (event.enqueuedAt || nowMs);
      var isPluckedChordIntent = articulation.family === 'plucked' && articulationQueue.length > 1;
      if (articulation.family === 'plucked' && (isPluckedChordIntent || elapsed >= captureWindow)) {
        event.playAfterFlushRelease = true;
        return true;
      }
      if (event.timer) window.clearTimeout(event.timer);
      removed = true;
      return false;
    });
    if (!articulationQueue.length && articulationFlushTimer) {
      window.clearTimeout(articulationFlushTimer);
      articulationFlushTimer = null;
    }
    return removed;
  }

  function sortArticulationEvents(events, articulation) {
    if ((articulation.order || '') === 'physical-low-to-high') {
      events.sort(function(a, b) {
        return physicalOrderValue(a) - physicalOrderValue(b) || a.sequence - b.sequence;
      });
    } else if ((articulation.order || '') === 'physical-high-to-low') {
      events.sort(function(a, b) {
        return physicalOrderValue(b) - physicalOrderValue(a) || a.sequence - b.sequence;
      });
    } else {
      events.sort(function(a, b) { return a.sequence - b.sequence; });
    }
    return events;
  }

  function startArticulatedVoice(event) {
    var canPlayReleasedCommittedPluck = event.playAfterFlushRelease && event.articulation && event.articulation.family === 'plucked';
    if (!state.heldNotes[event.key] && !canPlayReleasedCommittedPluck) {
      logEvent('audio', 'articulation skipped released ' + noteLabelFromMidi(event.midi) + ' mode=' + event.articulation.onsetMode);
      return;
    }
    startMidiVoice(event.key, event.midi, event.velocity, {
      expectedVoiceCount: event.expectedVoiceCount || 0,
      velocityLoadVoices: event.velocityLoadVoices || 0,
      articulationMode: event.articulation.onsetMode || '',
      articulationFamily: event.articulation.family || '',
      pressurePolicy: event.articulation.pressurePolicy || '',
      autoDampMs: event.articulation.autoDampMs || 0,
      releasedBeforeStart: !state.heldNotes[event.key]
    });
    var held = state.heldNotes[event.key];
    if (held && held.pressure !== event.velocity) {
      updateMidiVoicePressure(event.key, held.pressure);
    }
  }

  function applyPerformanceVolume() {
    var host = getSsliHost();
    var SL = host && host.SynthLab;
    if (!SL || !SL.audio) return false;
    var inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    ensureSsliPerformanceGain(SL, inst);
    return true;
  }

  function flushArticulationQueue() {
    if (articulationFlushTimer) {
      window.clearTimeout(articulationFlushTimer);
      articulationFlushTimer = null;
    }
    if (!articulationQueue.length) return;
    var events = articulationQueue.slice();
    articulationQueue = [];
    var articulation = events[0].articulation || immediateArticulation();
    sortArticulationEvents(events, articulation);
    var spacing = Math.max(0, Number(articulation.minInterOnsetMs || 0));
    var maxSpread = Math.max(0, Number(articulation.maxSpreadMs || 0));
    if (events.length > 1 && maxSpread > 0) spacing = Math.min(spacing, maxSpread / (events.length - 1));
    var labels = events.map(function(event) { return noteLabelFromMidi(event.midi); }).join(',');
    logEvent('audio', 'articulation flush mode=' + (articulation.onsetMode || 'immediate') + ' family=' + (articulation.family || 'unknown') + ' notes=' + labels + ' spacing=' + Math.round(spacing * 10) / 10 + 'ms');
    var activeAtFlush = heldSsliVoiceCount() + activeSsliOneShotCount();
    var expectedVoiceCount = activeAtFlush + events.length;
    events.forEach(function(event, index) {
      var delay = Math.round(index * spacing);
      event.expectedVoiceCount = expectedVoiceCount;
      event.velocityLoadVoices = Math.max(0, expectedVoiceCount);
      event.playAfterFlushRelease = event.playAfterFlushRelease || articulation.family === 'plucked';
      event.timer = window.setTimeout(function() {
        startArticulatedVoice(event);
      }, delay);
    });
  }

  function scheduleMidiVoiceStart(key, midi, velocity, cellId) {
    var articulation = selectedArticulation();
    var mode = articulation.onsetMode || 'immediate';
    if (mode === 'immediate' || mode === 'none') {
      startMidiVoice(key, midi, velocity);
      return;
    }
    removePendingArticulation(key);
    articulationQueue.push({
      key: key,
      midi: midi,
      velocity: velocity,
      cellId: cellId || '',
      articulation: articulation,
      sequence: articulationSequence++,
      enqueuedAt: Date.now()
    });
    if (articulationFlushTimer) window.clearTimeout(articulationFlushTimer);
    articulationFlushTimer = window.setTimeout(flushArticulationQueue, Math.max(0, Number(articulation.captureWindowMs || 0)));
    logEvent('audio', 'articulation queued ' + noteLabelFromMidi(midi) + ' mode=' + mode + ' family=' + (articulation.family || 'unknown') + ' capture=' + (articulation.captureWindowMs || 0) + 'ms');
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

  function setSsliMidiExpression(pressure, force) {
    pressure = Math.max(0, Math.min(127, Math.round(pressure || 0)));
    if (!force && lastSsliExpressionPressure !== null && Math.abs(pressure - lastSsliExpressionPressure) < SSLI_EXPRESSION_PRESSURE_STEP) {
      skippedSsliExpressionUpdates += 1;
      if (skippedSsliExpressionUpdates === 1 || skippedSsliExpressionUpdates % 16 === 0) {
        logEvent('audio', 'SSLI expression skipped pressure=' + pressure + ' last=' + lastSsliExpressionPressure + ' skipped=' + skippedSsliExpressionUpdates);
      }
      return true;
    }
    var host = getSsliHost();
    if (!host || !host.SynthLab || !host.SynthLab.audio || !host.SynthLab.audio.setExpression) return false;
    var SL = host.SynthLab;
    ensureSsliAudioReady(SL);
    var expression = pressureToSsliExpression(pressure);
    SL.audio.setExpression(expression.cutoffHz, expression.gain);
    lastSsliExpressionPressure = pressure;
    skippedSsliExpressionUpdates = 0;
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

  function updatePhysicalPerNotePressure(key, pressure) {
    var held = state.heldNotes[key];
    if (!held) return false;
    var nowMs = Date.now();
    var host = getSsliHost();
    var SL = host && host.SynthLab;
    var inst = SL && SL.audio && SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    var shapedPressure = Math.max(0, Math.min(127, Math.round(pressure || 0)));
    var voice = midiVoices[key];
    if (voice && shapedPressure > 0 && typeof voice.lastPhysicalPressure === 'number') {
      var pressureDelta = Math.abs(shapedPressure - voice.lastPhysicalPressure);
      var elapsed = nowMs - (voice.lastPhysicalPressureAt || 0);
      if (pressureDelta < PHYSICAL_PRESSURE_STEP && elapsed < PHYSICAL_PRESSURE_MIN_INTERVAL_MS) {
        voice.skippedPhysicalPressure = (voice.skippedPhysicalPressure || 0) + 1;
        if (voice.skippedPhysicalPressure === 1 || voice.skippedPhysicalPressure % 24 === 0) {
          logEvent('audio', 'SSLI physical per-note pressure skipped ' + noteLabelFromMidi(held.midi) + ' pressure=' + shapedPressure + ' last=' + voice.lastPhysicalPressure + ' skipped=' + voice.skippedPhysicalPressure);
        }
        return true;
      }
    }
    if (!SL || !SL.physical || !SL.physical.updateNotePressure) {
      logEvent('audio', 'SSLI physical per-note pressure unavailable ' + noteLabelFromMidi(held.midi) + ' pressure=' + shapedPressure + ' channel=' + (typeof held.channel === 'number' ? held.channel + 1 : held.channel));
      return false;
    }
    SL.physical.updateNotePressure(held.midi, shapedPressure, inst);
    if (voice) {
      voice.lastPhysicalPressure = shapedPressure;
      voice.lastPhysicalPressureAt = nowMs;
      voice.skippedPhysicalPressure = 0;
    }
    logEvent('audio', 'SSLI physical per-note pressure updated ' + noteLabelFromMidi(held.midi) + ' pressure=' + shapedPressure + ' channel=' + (typeof held.channel === 'number' ? held.channel + 1 : held.channel));
    return true;
  }

  function updateSsliExpressionFromHeldNotes() {
    var host = getSsliHost();
    if (host && host.SynthLab && getCurrentSsliInstrumentType(host.SynthLab) !== 'physical') {
      return false;
    }
    if (host && host.SynthLab && getCurrentSsliInstrumentType(host.SynthLab) === 'physical') {
      return false;
    }
    var strongest = strongestHeldMidiPressure();
    if (strongest > 0) {
      setSsliMidiExpression(strongest);
      return true;
    }
    clearSsliMidiExpression();
    return false;
  }

  function clearSsliMidiExpression() {
    if (lastSsliExpressionPressure === null) return false;
    var host = getSsliHost();
    if (host && host.SynthLab && host.SynthLab.audio && host.SynthLab.audio.clearExpression) {
      host.SynthLab.audio.clearExpression();
      lastSsliExpressionPressure = null;
      skippedSsliExpressionUpdates = 0;
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

  function cleanupSsliSustainedVoicesIfMidiIdle() {
    var hasHeldSsliVoice = Object.keys(midiVoices).some(function(key) {
      return midiVoices[key] && midiVoices[key].ssli;
    });
    if (hasHeldSsliVoice) return false;
    cleanupPhysicalEngineIfMidiIdle();
    var host = getSsliHost();
    if (!host || !host.SynthLab || !host.SynthLab.audio || !host.SynthLab.audio.stopAllSustained) return false;
    var SL = host.SynthLab;
    var activeCount = null;
    if (SL.audio.getActiveOscillators) {
      var activeOscs = SL.audio.getActiveOscillators();
      if (activeOscs && typeof activeOscs.size === 'number') activeCount = activeOscs.size;
    }
    if (activeCount === 0) return false;
    SL.audio.stopAllSustained();
    logEvent('audio', 'SSLI all sustained voices cleared after MIDI idle' + (activeCount !== null ? ' count=' + activeCount : ''));
    return true;
  }

  function cleanupPhysicalEngineIfMidiIdle() {
    var host = getSsliHost();
    if (!host || !host.SynthLab || !host.SynthLab.audio) return false;
    var SL = host.SynthLab;
    if (getCurrentSsliInstrumentType(SL) !== 'physical') return false;
    if (activeSsliOneShotCount() > 0) return false;
    return cleanupSsliEngineVoices(SL, 'after MIDI idle');
  }

  function reconcileSsliSustainedVoices(reason) {
    var host = getSsliHost();
    if (!host || !host.SynthLab || !host.SynthLab.audio || !host.SynthLab.audio.stopSustainedNote) return;
    var activeOscs = getSsliActiveOscillators();
    if (!activeOscs || !activeOscs.forEach) return;
    var liveMidis = localSsliVoiceMidiSet();
    activeOscs.forEach(function(node, midi) {
      if (!liveMidis[midi]) {
        host.SynthLab.audio.stopSustainedNote(Number(midi));
        logEvent('audio', 'reconciled stale SSLI voice ' + noteLabelFromMidi(Number(midi)) + ' after ' + reason);
      }
    });
  }

  function releaseDuplicateMidiVoices(midi, nextKey) {
    Object.keys(midiVoices).forEach(function(key) {
      var voice = midiVoices[key];
      if (!voice || voice.midi !== midi || key === nextKey) return;
      forgetHeldVoiceKey(key);
      releaseMidiVoice(key, true);
      logEvent('audio', 'released duplicate MIDI voice ' + noteLabelFromMidi(midi) + ' from ' + key);
    });
  }

  function startSustainedWithSsli(midi, velocity, options) {
    options = options || {};
    var host = getSsliHost();
    if (!host) {
      logEvent('audio', 'SSLI MIDI unavailable for ' + noteLabelFromMidi(midi) + ': missing runtime host');
      return false;
    }
    var SL = host.SynthLab;
    var readiness = describeSsliReadiness(SL, 'midi');
    if (readiness !== 'ready') {
      logEvent('audio', 'SSLI MIDI unavailable for ' + noteLabelFromMidi(midi) + ': ' + readiness);
      return false;
    }
    var fastMidiPath = shouldUseFastMidiPath(SL);
    if (!fastMidiPath) {
      ensureSsliAudioReady(SL);
      if (!applySelectedSsliPreset()) {
        logEvent('audio', 'SSLI MIDI unavailable for ' + noteLabelFromMidi(midi) + ': preset apply failed preset=' + state.soundPresetId);
        return false;
      }
      if (state.filterDirty) applySelectedSsliFilter();
      if (state.fxDirty) applySelectedSsliFxChain();
    }
    var inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    var preset = getSsliPresetPayload(SL);
    if (!fastMidiPath) verifySsliPresetRuntime(SL, preset, true);
    var instrumentType = getCurrentSsliInstrumentType(SL);
    var heldPhysicalVoices = instrumentType === 'physical' ? heldSsliVoiceCount() : 0;
    if (instrumentType === 'physical') {
      if (!fastMidiPath) ensureSsliPerformanceGain(SL, inst);
    } else {
      if (!fastMidiPath) ensureSsliPerformanceGain(SL, inst);
    }
    var physicalModel = instrumentType === 'physical' ? getCurrentPhysicalModel(SL) : '';
    var effectiveHeldPhysicalVoices = instrumentType === 'physical' ? (options.velocityLoadVoices || effectiveHeldPhysicalVoicesForVelocity(heldPhysicalVoices)) : 0;
    var playableVelocity = instrumentType === 'physical' ? playablePhysicalMidiVelocity(velocity, effectiveHeldPhysicalVoices) : playableSsliMidiVelocity(velocity);
    var fmVelocity = playableFmMidiVelocity(velocity);
    if (physicalModel === 'strike') {
      playableVelocity = Math.max(8, Math.round(playableVelocity * 0.25));
    }
    if (instrumentType === 'physical') {
      logEvent('audio', 'SSLI physical velocity shaped raw=' + Math.max(1, velocity || 1) + ' playable=' + playableVelocity + ' heldPhysical=' + heldPhysicalVoices + ' effectiveHeld=' + effectiveHeldPhysicalVoices + ' model=' + physicalModel + (options.expectedVoiceCount ? ' expectedVoices=' + options.expectedVoiceCount : ''));
    }
    logEvent('audio', 'SSLI call startSustainedNote midi=' + midi + ' note=' + noteLabelFromMidi(midi) + ' inst=' + inst + ' engine=' + instrumentType + ' activeBefore=' + heldSsliVoiceCount());
    if (instrumentType === 'fm' && SL.fm && SL.fm.noteOn) {
      SL.fm.noteOn(midi, fmVelocity, inst);
      if (SL.audio.getActiveOscillators) {
        SL.audio.getActiveOscillators().set(midi, { fm: true });
      }
      if (SL.audio.highlightNote) SL.audio.highlightNote(midi, true);
      logEvent('audio', 'SSLI FM direct sustain start ' + noteLabelFromMidi(midi) + ' velocity=' + fmVelocity);
    } else {
      SL.audio.startSustainedNote(midi, playableVelocity);
    }
    if (window.__exquisLatencyProbe && Array.isArray(window.__exquisLatencyProbe.starts)) {
      window.__exquisLatencyProbe.starts.push({ midi: midi, at: Date.now() });
    }
    if (instrumentType === 'physical') {
      logEvent('audio', 'SSLI physical note-on pressure captured ' + noteLabelFromMidi(midi) + ' pressure=' + Math.max(1, velocity || 1) + ' audioUpdate=note-on-velocity-only');
    }
    state.audioStatus = 'Audio: SSLI held ' + noteLabelFromMidi(midi) + '.';
    logEvent('audio', 'SSLI MIDI sustain start ' + noteLabelFromMidi(midi) + ' velocity=' + (instrumentType === 'fm' ? fmVelocity : playableVelocity) + ' pressure=' + Math.max(1, velocity || 1) + ' preset=' + state.soundPresetId);
    startAudioScope();
    render();
    return true;
  }

  function startPluckedOneShotWithSsli(midi, velocity, options) {
    options = options || {};
    var host = getSsliHost();
    if (!host) {
      logEvent('audio', 'SSLI plucked one-shot unavailable for ' + noteLabelFromMidi(midi) + ': missing runtime host');
      return false;
    }
    var SL = host.SynthLab;
    var readiness = describeSsliReadiness(SL, 'midi');
    if (readiness !== 'ready') {
      logEvent('audio', 'SSLI plucked one-shot unavailable for ' + noteLabelFromMidi(midi) + ': ' + readiness);
      return false;
    }
    if (!SL.physical || !SL.physical.noteOn) {
      logEvent('audio', 'SSLI plucked one-shot unavailable for ' + noteLabelFromMidi(midi) + ': missing SynthLab.physical.noteOn');
      return false;
    }
    var fastMidiPath = shouldUseFastMidiPath(SL);
    if (!fastMidiPath) {
      ensureSsliAudioReady(SL);
      if (!applySelectedSsliPreset()) {
        logEvent('audio', 'SSLI plucked one-shot unavailable for ' + noteLabelFromMidi(midi) + ': preset apply failed preset=' + state.soundPresetId);
        return false;
      }
      if (state.filterDirty) applySelectedSsliFilter();
      if (state.fxDirty) applySelectedSsliFxChain();
    }
    var inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    var preset = getSsliPresetPayload(SL);
    if (!fastMidiPath) verifySsliPresetRuntime(SL, preset, true);
    if (getCurrentSsliInstrumentType(SL) !== 'physical' || getCurrentPhysicalModel(SL) !== 'pluck') return false;
    if (!fastMidiPath) ensureSsliPerformanceGain(SL, inst);
    var requestedVoiceLoad = Math.max(0, Math.round(options.velocityLoadVoices || 0));
    var effectiveVoices = requestedVoiceLoad < PHYSICAL_UNSCALED_SIMULTANEOUS_VOICES ? 0 : requestedVoiceLoad;
    var playableVelocity = playablePhysicalMidiVelocity(velocity, effectiveVoices);
    var duration = Math.max(0.12, Math.min(0.6, Number(options.oneShotMs || SSLI_PHYSICAL_PLUCK_ONE_SHOT_MS) / 1000));
    SL.physical.noteOn(midi, playableVelocity, inst);
    state.audioStatus = 'Audio: SSLI plucked ' + noteLabelFromMidi(midi) + '.';
    logEvent('audio', 'SSLI plucked one-shot ' + noteLabelFromMidi(midi) + ' velocity=' + playableVelocity + ' pressure=' + Math.max(1, velocity || 1) + ' decay=natural preset=' + state.soundPresetId);
    startAudioScope();
    render();
    return true;
  }

  function stopSustainedWithSsli(midi) {
    var host = getSsliHost();
    if (!host || !host.SynthLab || !host.SynthLab.audio || !host.SynthLab.audio.stopSustainedNote) return false;
    var SL = host.SynthLab;
    var inst = SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
    var instrumentType = getCurrentSsliInstrumentType(SL);
    logEvent('audio', 'SSLI call stopSustainedNote midi=' + midi + ' note=' + noteLabelFromMidi(midi) + ' inst=' + inst + ' engine=' + instrumentType + ' activeBefore=' + heldSsliVoiceCount());
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

  function startMidiVoice(key, midi, velocity, options) {
    options = options || {};
    releaseMidiVoice(key, true);
    pruneMidiVoiceBudget(key);
    if (options.articulationFamily === 'plucked' && startPluckedOneShotWithSsli(midi, Math.max(1, velocity), options)) {
      var oneShotHost = getSsliHost();
      var oneShotSL = oneShotHost && oneShotHost.SynthLab;
      midiVoices[key] = {
        midi: midi,
        ssli: true,
        oneShot: true,
        instrumentType: oneShotSL ? getCurrentSsliInstrumentType(oneShotSL) : 'physical',
        startedAt: Date.now(),
        pressurePolicy: options.pressurePolicy || 'onset-only',
        articulationFamily: options.articulationFamily || 'plucked'
      };
      // Karplus-Strong plucks decay through the loop damping after excitation;
      // sending noteOff at a fixed timer artificially damps the string.
      // Original source: Karplus & Strong (1983), CMJ 7(2).
      midiVoices[key].oneShotNoteOffSent = true;
      logEvent('audio', 'SSLI plucked one-shot natural decay ' + noteLabelFromMidi(midi));
      midiVoices[key].oneShotCleanupTimer = window.setTimeout(function() {
        var voice = midiVoices[key];
        if (!voice || !voice.oneShot) return;
        if (state.heldNotes[key]) return;
        delete midiVoices[key];
        logMidiVoiceStats('after-one-shot-expire ' + noteLabelFromMidi(midi));
      }, Math.max(160, Number(options.oneShotMs || SSLI_PHYSICAL_PLUCK_ONE_SHOT_MS) + 120));
      logMidiVoiceStats('after-one-shot ' + noteLabelFromMidi(midi));
      return;
    }
    if (startSustainedWithSsli(midi, Math.max(1, velocity), options)) {
      var host = getSsliHost();
      var SL = host && host.SynthLab;
      midiVoices[key] = {
        midi: midi,
        ssli: true,
        instrumentType: SL ? getCurrentSsliInstrumentType(SL) : '',
        startedAt: Date.now(),
        pressurePolicy: options.pressurePolicy || '',
        articulationFamily: options.articulationFamily || ''
      };
      if (options.articulationFamily === 'plucked' && options.autoDampMs > 0) {
        midiVoices[key].autoDampTimer = window.setTimeout(function() {
          var voice = midiVoices[key];
          if (!voice || !voice.ssli || voice.articulationFamily !== 'plucked') return;
          stopSustainedWithSsli(voice.midi);
          voice.autoDampTimer = null;
          logEvent('audio', 'SSLI plucked auto-damp ' + noteLabelFromMidi(voice.midi) + ' after ' + options.autoDampMs + 'ms');
          reconcileSsliSustainedVoices('auto-damp ' + noteLabelFromMidi(voice.midi));
          logMidiVoiceStats('after-auto-damp ' + noteLabelFromMidi(voice.midi));
        }, Math.max(80, Number(options.autoDampMs || 0)));
      }
      reconcileSsliSustainedVoices('start ' + noteLabelFromMidi(midi));
      logMidiVoiceStats('after-start ' + noteLabelFromMidi(midi));
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
    var attackSeconds = Math.max(0.02, (adsr.a || 8) / 1000);
    var targetGain = 0.08 + level * 0.28;

    out.gain.setValueAtTime(0.0001, now);
    out.gain.exponentialRampToValueAtTime(targetGain, now + attackSeconds);
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
    logEvent('audio', 'MIDI voice start ' + noteLabelFromMidi(midi) + ' velocity=' + playableVelocity + ' pressure=' + Math.max(1, velocity || 1) + ' preset=' + state.soundPresetId + ' gain=' + targetGain.toFixed(3) + ' attack=' + Math.round(attackSeconds * 1000) + 'ms ctx=' + ctx.state);
    startAudioScope();
  }

  function updateMidiVoicePressure(key, pressure) {
    var voice = midiVoices[key];
    if (!voice) return;
    if (voice.ssli) {
      if (voice.pressurePolicy === 'onset-only') {
        if (!voice.skippedOnsetOnlyPressure) {
          voice.skippedOnsetOnlyPressure = true;
          logEvent('audio', 'SSLI plucked pressure ignored after onset ' + noteLabelFromMidi(voice.midi));
        }
        return;
      }
      var host = getSsliHost();
      if (host && host.SynthLab && getCurrentSsliInstrumentType(host.SynthLab) === 'physical') {
        updatePhysicalPerNotePressure(key, pressure);
        return;
      }
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
    releasePendingArticulation(key);
    var voice = midiVoices[key];
    if (voice && voice.ssli) {
      if (voice.oneShot) {
        if (immediate) {
          if (voice.oneShotCleanupTimer) {
            window.clearTimeout(voice.oneShotCleanupTimer);
            voice.oneShotCleanupTimer = null;
          }
          if (voice.oneShotNoteOffTimer) {
            window.clearTimeout(voice.oneShotNoteOffTimer);
            voice.oneShotNoteOffTimer = null;
          }
          if (!voice.oneShotNoteOffSent) {
            var oneShotHost = getSsliHost();
            var oneShotSL = oneShotHost && oneShotHost.SynthLab;
            if (oneShotSL && oneShotSL.physical && oneShotSL.physical.noteOff) {
              oneShotSL.physical.noteOff(voice.midi, oneShotSL.audio && oneShotSL.audio.getCurrentInstrument ? oneShotSL.audio.getCurrentInstrument() : 0);
              logEvent('audio', 'SSLI plucked one-shot note-off ' + noteLabelFromMidi(voice.midi) + ' immediate');
            }
          }
          delete midiVoices[key];
        } else if (voice.oneShotNoteOffSent) {
          delete midiVoices[key];
        }
        clearSsliMidiExpressionIfIdle();
        logMidiVoiceStats('after-one-shot-release ' + noteLabelFromMidi(voice.midi));
        return;
      }
      if (voice.autoDampTimer) {
        window.clearTimeout(voice.autoDampTimer);
        voice.autoDampTimer = null;
      }
      stopSustainedWithSsli(voice.midi);
      delete midiVoices[key];
      reconcileSsliSustainedVoices('release ' + noteLabelFromMidi(voice.midi));
      cleanupSsliSustainedVoicesIfMidiIdle();
      clearSsliMidiExpressionIfIdle();
      logMidiVoiceStats('after-stop ' + noteLabelFromMidi(voice.midi));
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
    scheduleMidiVoiceStart(key, cell.midi, pressure, cell.id);
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
    pendingLogs = [];
    if (logFlushTimer) {
      window.clearTimeout(logFlushTimer);
      logFlushTimer = null;
    }
    resetVisualMidi();
    if (els.consolePanel) els.consolePanel.classList.add('expanded');
    if (els.diagnosticLog) els.diagnosticLog.textContent = 'Ready.';
    logEvent('console', 'reset');
    render();
  }

  function copyConsole() {
    var text = allLogText();
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
      els.consolePanel.classList.remove('expanded');
      logEvent('console', 'collapsed');
    }
  }

  function expandConsole() {
    if (els.consolePanel) {
      els.consolePanel.hidden = false;
      els.consolePanel.classList.add('expanded');
      if (els.diagnosticLog) els.diagnosticLog.scrollTop = els.diagnosticLog.scrollHeight;
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
    var scale = getScale();
    var candidates = cells.filter(function(cell) {
      return cell.pc === state.tonicPc;
    });
    if (state.exerciseId === 'two_octaves') {
      var preferredTwoOctaveRootMidi = 36 + state.tonicPc;
      return candidates.sort(function(a, b) {
        var aSupported = supportsAscendingOctaves(cells, scale, a, 2);
        var bSupported = supportsAscendingOctaves(cells, scale, b, 2);
        return (bSupported ? 1 : 0) - (aSupported ? 1 : 0) || Math.abs(a.midi - preferredTwoOctaveRootMidi) - Math.abs(b.midi - preferredTwoOctaveRootMidi) || centerScore(a) - centerScore(b) || a.midi - b.midi;
      });
    }
    var supported = candidates.filter(function(cell) {
      return supportsAscendingOctaves(cells, scale, cell, 1);
    });
    if (!supported.length) supported = candidates;
    var byMidi = supported.slice().sort(function(a, b) {
      return a.midi - b.midi || centerScore(a) - centerScore(b);
    });
    var preferredRootMidi = state.octaveSide === 'lower' ? byMidi[0].midi : byMidi[byMidi.length - 1].midi;
    return supported.sort(function(a, b) {
      var aSupported = state.exerciseId === 'two_octaves' && supportsAscendingOctaves(cells, scale, a, 2);
      var bSupported = state.exerciseId === 'two_octaves' && supportsAscendingOctaves(cells, scale, b, 2);
      return (bSupported ? 1 : 0) - (aSupported ? 1 : 0) || Math.abs(a.midi - preferredRootMidi) - Math.abs(b.midi - preferredRootMidi) || centerScore(a) - centerScore(b) || a.midi - b.midi;
    });
  }

  function hasCellForMidi(cells, midi) {
    for (var i = 0; i < cells.length; i++) {
      if (cells[i].midi === midi) return true;
    }
    return false;
  }

  function supportsAscendingOctaves(cells, scale, root, octaveCount) {
    var totalOctaves = Math.max(1, octaveCount || 1);
    for (var octaveIndex = 0; octaveIndex < totalOctaves; octaveIndex++) {
      for (var d = 0; d < scale.intervals.length; d++) {
        if (!hasCellForMidi(cells, root.midi + scale.intervals[d] + octaveIndex * 12)) return false;
      }
    }
    return hasCellForMidi(cells, root.midi + totalOctaves * 12);
  }

  function rootSupportsCurrentExercise(cells, scale, root) {
    if (!root) return false;
    if (state.exerciseId === 'two_octaves') return supportsAscendingOctaves(cells, scale, root, 2);
    return supportsAscendingOctaves(cells, scale, root, 1);
  }

  function selectedRoot(cells) {
    var roots = rootCandidates(cells);
    if (!roots.length) return null;
    var scale = getScale();
    for (var i = 0; i < roots.length; i++) {
      if (roots[i].id === state.rootCellId && rootSupportsCurrentExercise(cells, scale, roots[i])) return roots[i];
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
      option.textContent = noteName(roots[i].midi) + octave(roots[i].midi) + ' / r' + (roots[i].row + 1) + ' k' + (roots[i].col + 1);
      els.root.appendChild(option);
    }
    if (roots.length) {
      var scale = getScale();
      if (!roots.some(function(root) { return root.id === state.rootCellId && rootSupportsCurrentExercise(cells, scale, root); })) state.rootCellId = roots[0].id;
      els.root.value = state.rootCellId;
    }
  }

  function developerZoneCaptured(zone) {
    var mask = state.exquisDeveloperMask || 0;
    if (zone === 'pads') return (mask & EXQUIS_DEVELOPER_PADS_MASK) !== 0;
    if (zone === 'encoders') return (mask & EXQUIS_DEVELOPER_ENCODERS_MASK) !== 0;
    if (zone === 'slider') return (mask & 0x04) !== 0;
    if (zone === 'updown') return (mask & 0x08) !== 0;
    if (zone === 'settings') return (mask & EXQUIS_DEVELOPER_SETTINGS_SOUND_MASK) !== 0;
    if (zone === 'other') return (mask & EXQUIS_DEVELOPER_LEGACY_PROBE_MASK) !== 0;
    return false;
  }

  function developerMaskLabel(mask) {
    mask = mask || 0;
    if (!mask) return 'Developer zones: normal';
    var labels = [];
    if (mask & EXQUIS_DEVELOPER_PADS_MASK) labels.push('pads');
    if (mask & EXQUIS_DEVELOPER_ENCODERS_MASK) labels.push('encoders');
    if (mask & 0x04) labels.push('slider');
    if (mask & 0x08) labels.push('up/down');
    if (mask & EXQUIS_DEVELOPER_SETTINGS_SOUND_MASK) labels.push('settings/sound');
    if (mask & EXQUIS_DEVELOPER_LEGACY_PROBE_MASK) labels.push('other buttons');
    return 'Developer zones: ' + labels.join(', ') + ' (0x' + mask.toString(16).toUpperCase().padStart(2, '0') + ')';
  }

  function renderEdgeControls() {
    if (!els.edgeTopControls || !els.edgeBottomControls) return;
    clearChildren(els.edgeTopControls);
    clearChildren(els.edgeBottomControls);
    if (els.edgeControlStatus) els.edgeControlStatus.textContent = developerMaskLabel(state.exquisDeveloperMask);

    var encoderRow = document.createElement('div');
    encoderRow.className = 'edge-encoder-row';
    encoderRow.setAttribute('data-testid', 'edge-encoder-row');
    ['enc1', 'enc2', 'enc3', 'enc4'].forEach(function(id) {
      encoderRow.appendChild(createEdgeControlElement(EXQUIS_EDGE_BY_ID[id]));
    });
    els.edgeTopControls.appendChild(encoderRow);

    var deck = document.createElement('div');
    deck.className = 'edge-bottom-deck';
    deck.setAttribute('data-testid', 'edge-bottom-deck');
    var selectGroup = document.createElement('div');
    selectGroup.className = 'edge-select-group';
    selectGroup.setAttribute('data-testid', 'edge-select-group');
    selectGroup.appendChild(createEdgeControlElement(EXQUIS_EDGE_BY_ID.down));
    selectGroup.appendChild(createEdgeControlElement(EXQUIS_EDGE_BY_ID.up));
    var sliderGroup = document.createElement('div');
    sliderGroup.className = 'edge-slider-group';
    sliderGroup.setAttribute('data-testid', 'edge-slider-group');
    sliderGroup.appendChild(createEdgeControlElement(EXQUIS_EDGE_BY_ID.slider));
    var undoGroup = document.createElement('div');
    undoGroup.className = 'edge-undo-group';
    undoGroup.setAttribute('data-testid', 'edge-undo-group');
    undoGroup.appendChild(createEdgeControlElement(EXQUIS_EDGE_BY_ID.undo));
    undoGroup.appendChild(createEdgeControlElement(EXQUIS_EDGE_BY_ID.redo));
    deck.appendChild(selectGroup);
    deck.appendChild(sliderGroup);
    deck.appendChild(undoGroup);

    var actionRow = document.createElement('div');
    actionRow.className = 'edge-action-row';
    actionRow.setAttribute('data-testid', 'edge-action-row');
    ['settings', 'sound', 'record', 'loop', 'clips', 'playStop'].forEach(function(id) {
      actionRow.appendChild(createEdgeControlElement(EXQUIS_EDGE_BY_ID[id]));
    });

    els.edgeBottomControls.appendChild(deck);
    els.edgeBottomControls.appendChild(actionRow);
  }

  function createEdgeControlElement(control) {
      var item = document.createElement('div');
      var captured = developerZoneCaptured(control.zone);
      var active = state.activeEdgeControlId === control.id || state.lastEdgeControlId === control.id;
      item.className = 'edge-control edge-' + control.kind + (captured ? ' captured' : '') + (active ? ' active' : '');
      item.setAttribute('data-testid', 'edge-control');
      item.setAttribute('data-edge-id', control.id);
      item.setAttribute('data-zone', control.zone);
      item.setAttribute('aria-label', control.label + ', ' + control.detail + ', LED ' + control.led + (captured ? ', developer captured' : ', normal'));
      var visual = document.createElement('span');
      visual.className = 'edge-visual';
      visual.setAttribute('aria-hidden', 'true');
      var name = document.createElement('span');
      name.className = 'edge-name';
      name.textContent = control.label;
      var meta = document.createElement('span');
      meta.className = 'edge-meta';
      var ccText = typeof control.cc === 'number' ? ' CC' + control.cc : '';
      var clickText = typeof control.clickCc === 'number' ? ' / click ' + control.clickCc : '';
      meta.textContent = 'LED ' + control.led + ccText + clickText;
      var detail = document.createElement('span');
      detail.className = 'edge-detail';
      detail.textContent = control.detail;
      var label = document.createElement('span');
      label.className = 'edge-label';
      label.appendChild(name);
      label.appendChild(meta);
      label.appendChild(detail);
      item.appendChild(visual);
      item.appendChild(label);
      if (active && state.lastEdgeControlValue) {
        var value = document.createElement('span');
        value.className = 'edge-value';
        value.textContent = state.lastEdgeControlValue;
        label.appendChild(value);
      }
      return item;
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

  function bestCellForTarget(cells, pc, targetMidi, anchor, preferredCellsById) {
    var best = null;
    var bestScore = Infinity;
    for (var i = 0; i < cells.length; i++) {
      if (cells[i].pc !== pc) continue;
      var exactMidiPenalty = cells[i].midi === targetMidi ? 0 : 10000;
      var distance = Math.abs(cells[i].midi - targetMidi) * 24;
      var preferredPenalty = preferredCellsById && !preferredCellsById[cells[i].id] ? 1000 : 0;
      var spatial = anchor ? (Math.abs(cells[i].row - anchor.row) + Math.abs(cells[i].col - anchor.col)) : centerScore(cells[i]) * 10;
      var chainPenalty = anchor && !isInnerChainCell(cells[i], anchor) ? 100 : 0;
      var centerPreference = centerScore(cells[i]) * 12;
      var score = exactMidiPenalty + distance + preferredPenalty + chainPenalty + spatial + centerPreference;
      if (score < bestScore) {
        best = cells[i];
        bestScore = score;
      }
    }
    return best;
  }

  function buildAscendingScalePath(cells, scale, octaveCount) {
    var root = selectedRoot(cells);
    if (!root) return [];
    var path = [];
    var preferredCellsById = getLitPracticeCells(cells, scale, root);
    var totalOctaves = Math.max(1, octaveCount || 1);
    for (var octaveIndex = 0; octaveIndex < totalOctaves; octaveIndex++) {
      for (var d = 0; d < scale.intervals.length; d++) {
        var interval = scale.intervals[d] + octaveIndex * 12;
        var targetMidi = root.midi + interval;
        var pc = mod(state.tonicPc + interval, 12);
        var cell = interval === 0 ? root : bestCellForTarget(cells, pc, targetMidi, root, preferredCellsById);
        if (cell && cell.midi === targetMidi) {
          var pathCell = {};
          Object.keys(cell).forEach(function(key) { pathCell[key] = cell[key]; });
          path.push(pathCell);
        }
      }
    }
    var octaveCell = bestCellForTarget(cells, root.pc, root.midi + totalOctaves * 12, root, preferredCellsById);
    if (octaveCell && octaveCell.midi === root.midi + totalOctaves * 12) {
      var octavePathCell = {};
      Object.keys(octaveCell).forEach(function(key) { octavePathCell[key] = octaveCell[key]; });
      path.push(octavePathCell);
    }
    return path;
  }

  function buildRootToOctavePath(cells, scale) {
    return buildAscendingScalePath(cells, scale, 1);
  }

  function clonePathCell(cell) {
    var pathCell = {};
    Object.keys(cell).forEach(function(key) { pathCell[key] = cell[key]; });
    return pathCell;
  }

  function getPracticePath(cells, scale) {
    var basePath = buildRootToOctavePath(cells, scale);
    if (state.exerciseId === 'two_octaves') {
      return buildAscendingScalePath(cells, scale, 2);
    }
    if (state.exerciseId === 'inner_ladder' && basePath.length > 1) {
      var ladder = basePath.map(clonePathCell);
      for (var i = basePath.length - 2; i >= 0; i--) {
        ladder.push(clonePathCell(basePath[i]));
      }
      return ladder;
    }
    if (state.exerciseId === 'root_returns' && basePath.length > 1) {
      var root = clonePathCell(basePath[0]);
      var returns = [root];
      for (var j = 1; j < basePath.length; j++) {
        returns.push(clonePathCell(basePath[j]));
        if (j < basePath.length - 1) returns.push(clonePathCell(root));
      }
      return returns;
    }
    return basePath;
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
    var safeBottom = stageBox.bottom;
    ['[data-testid="console-panel"]', '[data-testid="build-version"]'].forEach(function(selector) {
      var overlay = document.querySelector(selector);
      if (!overlay || !overlay.getBoundingClientRect) return;
      var box = overlay.getBoundingClientRect();
      var overlapsStage = box.right > stageBox.left && box.left < stageBox.right && box.bottom > stageBox.top && box.top < stageBox.bottom;
      if (overlapsStage && box.top > stageBox.top) safeBottom = Math.min(safeBottom, box.top - 8);
    });
    var topControls = els.edgeTopControls && els.edgeTopControls.closest ? els.edgeTopControls.closest('.edge-controls-top') : null;
    var bottomControls = els.edgeBottomControls && els.edgeBottomControls.closest ? els.edgeBottomControls.closest('.edge-controls-bottom') : null;
    var topHeight = topControls && topControls.getBoundingClientRect ? topControls.getBoundingClientRect().height : 0;
    var bottomHeight = bottomControls && bottomControls.getBoundingClientRect ? bottomControls.getBoundingClientRect().height : 0;
    var topWidth = topControls && topControls.getBoundingClientRect ? topControls.getBoundingClientRect().width : 0;
    var bottomWidth = bottomControls && bottomControls.getBoundingClientRect ? bottomControls.getBoundingClientRect().width : 0;
    if (state.orientation === 'horizontal') {
      return {
        width: Math.max(0, stageBox.width - topWidth - bottomWidth - 44),
        height: Math.max(0, safeBottom - headerBox.bottom - 4)
      };
    }
    return {
      width: Math.max(0, stageBox.width - 20),
      height: Math.max(0, safeBottom - headerBox.bottom - topHeight - bottomHeight - 66)
    };
  }

  function getKeyboardScale(baseWidth, baseHeight) {
    var available = getKeyboardAvailableSpace();
    if (!available.width || !available.height) return 1;
    var minScale = state.orientation === 'vertical' ? 0.52 : 0.72;
    return Math.max(minScale, Math.min(1.9, available.width / baseWidth, available.height / baseHeight));
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

  function midiCellDebug(cell) {
    if (!cell) return 'cell=pitch-only';
    return 'cell=' + cell.id + ' cellLabel=' + cell.label + octave(cell.midi) + ' row=' + cell.row + ' col=' + cell.col;
  }

  function logRecentMidiChord() {
    recentMidiChordTimer = null;
    if (recentMidiChordNotes.length < 2) {
      recentMidiChordNotes = [];
      return;
    }
    var notes = recentMidiChordNotes.slice();
    recentMidiChordNotes = [];
    notes.sort(function(a, b) { return a.at - b.at; });
    logEvent('midi', 'note-on chord window notes=' + notes.map(function(note) {
      return note.label + '@ch' + note.channel + ':' + note.cellId + ':v' + note.velocity;
    }).join(','));
  }

  function rememberRecentMidiChordNote(midi, velocity, channel, cell) {
    var now = Date.now();
    recentMidiChordNotes = recentMidiChordNotes.filter(function(note) { return now - note.at <= 55; });
    recentMidiChordNotes.push({
      label: noteLabelFromMidi(midi),
      midi: midi,
      velocity: velocity,
      channel: channel + 1,
      cellId: cell ? cell.id : 'pitch-only',
      at: now
    });
    if (recentMidiChordTimer) window.clearTimeout(recentMidiChordTimer);
    recentMidiChordTimer = window.setTimeout(logRecentMidiChord, 60);
  }

  function setFeedback(message, kind) {
    state.feedback = message;
    state.feedbackKind = kind || 'neutral';
  }

  function setMode(mode) {
    state.mode = mode === 'play' ? 'play' : 'practice';
    state.step = 0;
    if (els.mode) els.mode.value = state.mode;
    if (els.practiceMode) {
      els.practiceMode.classList.toggle('active', state.mode === 'practice');
      els.practiceMode.setAttribute('aria-pressed', state.mode === 'practice' ? 'true' : 'false');
    }
    if (els.playMode) {
      els.playMode.classList.toggle('active', state.mode === 'play');
      els.playMode.setAttribute('aria-pressed', state.mode === 'play' ? 'true' : 'false');
    }
    if (state.mode === 'play') {
      setFeedback('Play mode: free surface, scoring paused.', 'live');
    } else {
      setFeedback('Practice mode: follow the current target.', 'neutral');
    }
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
    var ageMs = held && held.startedAt ? Date.now() - held.startedAt : 999;
    if (held && ageMs >= 0 && ageMs < EXQUIS_MIN_MIDI_HOLD_MS && !pendingShortNoteReleases[key]) {
      pendingShortRawReleases[rawMidi] = Date.now();
      pendingShortNoteReleases[key] = window.setTimeout(function() {
        delete pendingShortNoteReleases[key];
        delete pendingShortRawReleases[rawMidi];
        releaseMidiNote(rawMidi, channel);
      }, EXQUIS_MIN_MIDI_HOLD_MS - ageMs);
      logEvent('midi', 'note-off delayed short hold ' + noteLabelFromMidi(midi) + ' midi=' + midi + ' raw=' + rawMidi + ' channel=' + (channel + 1) + ' age=' + Math.round(ageMs) + 'ms');
      return;
    }
    delete state.heldNotes[key];
    if (channel !== null && state.channelNotes[channel] === midi) {
      delete state.channelNotes[channel];
    }
    recentMidiNoteOffs[rawMidi] = Date.now();
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
    var now = Date.now();
    if (now - lastMidiPressureLogAt >= 120 || pressure === 0) {
      logEvent('midi', source + ' ' + noteLabelFromMidi(midi) + ' pressure=' + pressure);
      lastMidiPressureLogAt = now;
    }
    if (now - lastMidiPressureRenderAt >= 50 || pressure === 0) {
      render();
      lastMidiPressureRenderAt = now;
    }
  }

  function isReleaseBounceNoteOn(rawMidi, velocity) {
    if (pendingShortRawReleases[rawMidi]) return velocity <= 16;
    if (velocity > 2) return false;
    var lastOffAt = recentMidiNoteOffs[rawMidi];
    return typeof lastOffAt === 'number' && Date.now() - lastOffAt <= 45;
  }

  function handleMidiNote(rawMidi, velocity, channel) {
    var midi = displayMidiFromRaw(rawMidi);
    if (isReleaseBounceNoteOn(rawMidi, velocity)) {
      logEvent('midi', 'note-on ignored release bounce ' + noteLabelFromMidi(midi) + ' midi=' + midi + ' raw=' + rawMidi + ' velocity=' + velocity + ' channel=' + (channel + 1));
      return;
    }
    if (window.__exquisLatencyProbe && Array.isArray(window.__exquisLatencyProbe.inputs)) {
      window.__exquisLatencyProbe.inputs.push({ midi: midi, at: Date.now() });
    }
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
    if (pendingShortNoteReleases[heldKey]) {
      window.clearTimeout(pendingShortNoteReleases[heldKey]);
      delete pendingShortNoteReleases[heldKey];
      delete pendingShortRawReleases[rawMidi];
    }
    if (channel !== null && typeof state.channelNotes[channel] === 'number' && state.channelNotes[channel] !== midi) {
      var previousMidi = state.channelNotes[channel];
      var previousKey = voiceKey(channel, previousMidi);
      delete state.heldNotes[previousKey];
      releaseMidiVoice(previousKey, true);
      logEvent('audio', 'released previous channel voice ' + noteLabelFromMidi(previousMidi) + ' before ' + noteLabelFromMidi(midi));
    }
    releaseDuplicateMidiVoices(midi, heldKey);
    state.heldNotes[heldKey] = {
      midi: midi,
      rawMidi: rawMidi,
      pc: mod(midi, 12),
      velocity: velocity,
      pressure: velocity,
      cellId: hitCell ? hitCell.id : '',
      channel: channel,
      startedAt: Date.now()
    };
    if (channel !== null) state.channelNotes[channel] = midi;
    scheduleMidiVoiceStart(heldKey, midi, velocity, hitCell ? hitCell.id : '');
    logEvent('midi', 'note-on ' + noteLabelFromMidi(midi) + ' midi=' + midi + ' raw=' + rawMidi + ' velocity=' + velocity + ' channel=' + (channel + 1) + ' match=' + (hitCell ? hitCell.id : 'pitch-only') + ' ' + midiCellDebug(hitCell));
    rememberRecentMidiChordNote(midi, velocity, channel, hitCell);

    if (state.mode !== 'practice') {
      setFeedback('Play mode: ' + noteLabelFromMidi(midi) + ' is sounding freely.', 'live');
    } else if (expected && mod(midi, 12) === expected.pc) {
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
    if (data[0] === 0xF0) {
      handleExquisSysex(data);
      return;
    }
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
    } else if (status === 0xB0 && channel === 15) {
      var officialEdge = EXQUIS_EDGE_BY_OFFICIAL_ID[midi];
      if (midi >= 110 && midi <= 113) {
        var delta = velocity - 64;
        rememberEdgeControl(officialEdge || null, 'delta ' + delta);
        logEvent('midi', 'Exquis dial encoder=' + midi + ' ' + (officialEdge ? officialEdge.label + ' ' : '') + 'delta=' + delta + ' raw=' + velocity);
        state.midiActivity = 'Activity: ' + (officialEdge ? officialEdge.label : 'dial ' + midi) + ' delta ' + delta;
        render();
      } else if (officialEdge) {
        rememberEdgeControl(officialEdge, velocity >= 64 ? 'on' : 'off');
        logEvent('midi', 'Exquis edge control id=' + midi + ' ' + officialEdge.label + ' value=' + velocity);
        state.midiActivity = 'Activity: ' + officialEdge.label + ' value ' + velocity;
        render();
      } else {
        logEvent('midi', 'Exquis ch16 control id=' + midi + ' value=' + velocity);
      }
    } else if (state.exquisDialListenEnabled && status === 0xB0 && channel === 0 && handleExquisSettingsControl(midi, velocity)) {
      return;
    } else if (state.exquisDialListenEnabled) {
      logEvent('midi', 'Exquis dial raw status=0x' + data[0].toString(16).toUpperCase().padStart(2, '0') + ' channel=' + (channel + 1) + ' data=' + Array.prototype.slice.call(data).join(','));
    }
  }

  function rememberEdgeControl(control, value) {
    if (!control) return;
    state.activeEdgeControlId = control.id;
    state.lastEdgeControlId = control.id;
    state.lastEdgeControlValue = value || '';
  }

  function handleExquisSettingsControl(cc, value) {
    var control = EXQUIS_EDGE_BY_CC[cc];
    if (control) {
      rememberEdgeControl(control, String(value));
      var dialIndex = cc - 40;
      if (cc === 42 && value >= 0 && value <= 11) {
        logEvent('midi', 'Exquis settings ' + control.label + ' root value=' + value + ' note=' + TONICS[value].name);
        updateTonicFromHardwareRoot(value, 'Settings Encoder 2');
      } else if (cc === 43) {
        logEvent('midi', 'Exquis settings ' + control.label + ' scale-number=' + value);
        updateScaleFromHardwareNumber(value, 'Settings Encoder 3');
      } else {
        logEvent('midi', 'Exquis settings ' + control.label + ' cc=' + cc + ' value=' + value);
        state.midiActivity = 'Activity: ' + control.label + ' value ' + value;
        render();
      }
      return true;
    }
    control = EXQUIS_EDGE_BY_CLICK_CC[cc];
    if (control) {
      rememberEdgeControl(control, value >= 64 ? 'click on' : 'click off');
      logEvent('midi', 'Exquis settings ' + control.label + ' click value=' + value);
      state.midiActivity = 'Activity: ' + control.label + ' click ' + value;
      render();
      return true;
    }
    return false;
  }

  function midiInputLabel(input) {
    var name = input && input.name ? input.name : 'Unnamed MIDI input';
    var manufacturer = input && input.manufacturer ? input.manufacturer : '';
    return manufacturer && name.indexOf(manufacturer) < 0 ? name + ' (' + manufacturer + ')' : name;
  }

  function isExquisMidiDevice(device) {
    var label = ((device && device.name ? device.name : '') + ' ' + (device && device.manufacturer ? device.manufacturer : '')).toLowerCase();
    return label.indexOf('exquis') >= 0 || label.indexOf('intuitive') >= 0;
  }

  function midiDeviceLabel(device) {
    return midiInputLabel(device);
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

  function getMidiOutputs(access) {
    var outputs = [];
    if (!access || !access.outputs) return outputs;
    access.outputs.forEach(function(output) {
      outputs.push(output);
    });
    outputs.sort(function(a, b) {
      return midiDeviceLabel(a).localeCompare(midiDeviceLabel(b));
    });
    return outputs;
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

  function chooseMidiOutput(access) {
    var chosen = null;
    var outputs = getMidiOutputs(access);
    for (var i = 0; i < outputs.length; i++) {
      var output = outputs[i];
      var name = ((output.name || '') + ' ' + (output.manufacturer || '')).toLowerCase();
      if (state.selectedMidiOutputId && output.id === state.selectedMidiOutputId) {
        chosen = output;
        break;
      }
      if (!chosen || name.indexOf('exquis') >= 0 || name.indexOf('intuitive') >= 0) {
        chosen = output;
      }
    }
    return chosen;
  }

  function disconnectMidiInput() {
    if (midiInput) midiInput.onmidimessage = null;
    midiInput = null;
  }

  function connectMidiOutput(output) {
    midiOutput = output || null;
    if (midiOutput) {
      state.selectedMidiOutputId = midiOutput.id || '';
      logEvent('midi', 'output ready ' + midiDeviceLabel(midiOutput) + ' id=' + (midiOutput.id || 'unknown'));
    }
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
    var outputs = getMidiOutputs(access);
    state.midiInputs = inputs.map(function(input) {
      return {
        id: input.id || midiInputLabel(input),
        label: midiInputLabel(input),
        state: input.state || '',
        connection: input.connection || ''
      };
    });
    state.midiOutputs = outputs.map(function(output) {
      return {
        id: output.id || midiDeviceLabel(output),
        label: midiDeviceLabel(output),
        state: output.state || '',
        connection: output.connection || ''
      };
    });
    if (inputs.length && !state.selectedMidiId) {
      var preferred = chooseMidiInput(access);
      state.selectedMidiId = preferred && preferred.id ? preferred.id : inputs[0].id;
    }
    if (outputs.length && !state.selectedMidiOutputId) {
      var preferredOutput = chooseMidiOutput(access);
      state.selectedMidiOutputId = preferredOutput && preferredOutput.id ? preferredOutput.id : outputs[0].id;
    }
    return inputs;
  }

  function sendExquisSysex(command, payload, reason) {
    if (!state.exquisSyncEnabled || !midiOutput || !midiOutput.send) return false;
    var bytes = buildExquisSysex(command, payload || []);
    return sendRawMidi(bytes, 'Exquis sync send ' + (reason || ('cmd=' + command)));
  }

  function sendOfficialPadsDeveloperMode(enabled, reason) {
    return sendRawMidi(buildExquisSysex(0x00, [enabled ? EXQUIS_DEVELOPER_PADS_MASK : 0x00]), 'Exquis sync send ' + reason);
  }

  function sendOfficialDialListenDeveloperMode(enabled, reason) {
    return sendRawMidi(buildExquisSysex(0x00, [enabled ? EXQUIS_DEVELOPER_DIAL_LISTEN_MASK : 0x00]), 'Exquis sync send ' + reason);
  }

  function beginOfficialKeyModeTransaction(reason) {
    return sendOfficialPadsDeveloperMode(true, (reason || 'native-keymode') + ' developer-mode pads=0x01');
  }

  function endOfficialKeyModeTransaction(reason) {
    if (state.exquisDialListenEnabled) return true;
    return sendOfficialPadsDeveloperMode(false, (reason || 'native-keymode') + ' developer-mode off');
  }

  function sendRawMidi(bytes, reason) {
    if (!midiOutput || !midiOutput.send) return false;
    try {
      midiOutput.send(bytes);
      if (bytes && bytes.length >= 7 && bytes[0] === 0xF0 && bytes[1] === 0x00 && bytes[2] === 0x21 && bytes[3] === 0x7E && bytes[4] === 0x7F && bytes[5] === 0x00) {
        state.exquisDeveloperMask = clamp7Bit(bytes[6]);
      }
      if (reason) logEvent('midi', reason + ' bytes=' + bytesToHex(bytes));
      return true;
    } catch (err) {
      state.exquisSyncStatus = 'Exquis sync: send failed';
      logEvent('midi', reason + ' failed: ' + (err && err.message ? err.message : err));
      return false;
    }
  }

  function sendOfficialProbeMask(mask, label) {
    sendRawMidi(buildExquisSysex(0x00, [mask]), 'Exquis probe official setup ' + label);
    sendRawMidi(buildExquisSysex(0x06, []), 'Exquis probe official root-readback ' + label);
    sendRawMidi(buildExquisSysex(0x07, []), 'Exquis probe official scale-readback ' + label);
    sendRawMidi(buildExquisSysex(0x03, []), 'Exquis probe official refresh ' + label);
  }

  function sendNativeWriteProbeMask(mask, label) {
    var rootPc = mod(state.tonicPc, 12);
    var scaleIndex = exquisScaleNumberForScaleId(state.scaleId);
    sendRawMidi(buildExquisSysex(0x00, [mask]), 'Exquis native probe setup ' + label);
    sendRawMidi(buildExquisSysex(0x06, [rootPc]), 'Exquis native probe root=' + getTonicName() + ' ' + label);
    sendRawMidi(buildExquisSysex(0x07, [scaleIndex]), 'Exquis native probe scale=' + state.scaleId + ' index=' + scaleIndex + ' ' + label);
    sendRawMidi(buildExquisSysex(0x03, []), 'Exquis native probe refresh ' + label);
    sendRawMidi(buildExquisSysex(0x06, []), 'Exquis native probe root-readback ' + label);
    sendRawMidi(buildExquisSysex(0x07, []), 'Exquis native probe scale-readback ' + label);
    sendRawMidi(buildExquisSysex(0x00, [0x00]), 'Exquis native probe developer-mode off ' + label);
  }

  function exquisLegacyPadId(cell) {
    var id = 0;
    var count = EXQUIS_NOTE_ROWS[cell.row].length;
    if (state.legacyMap === 'top_left' || state.legacyMap === 'top_right') {
      for (var topRow = 0; topRow < cell.row; topRow++) id += EXQUIS_NOTE_ROWS[topRow].length;
    } else {
      for (var bottomRow = EXQUIS_NOTE_ROWS.length - 1; bottomRow > cell.row; bottomRow--) id += EXQUIS_NOTE_ROWS[bottomRow].length;
    }
    if (state.legacyMap === 'bottom_right' || state.legacyMap === 'top_right') return id + (count - 1 - cell.col);
    return id + cell.col;
  }

  function exquisLegacyColorForCell(cell, scale) {
    if (cell.pc === state.tonicPc) return [0x7F, 0x5F, 0x3F];
    if (isScalePc(cell.pc, scale)) return [0x38, 0x1D, 0x41];
    return [0x00, 0x00, 0x00];
  }

  function sendExquisLegacyKeepalive(reason) {
    return sendRawMidi(buildExquisLegacySysex(null, []), reason || '');
  }

  function startExquisLegacyKeepalive() {
    if (exquisLegacyKeepaliveTimer) return;
    exquisLegacyKeepaliveTimer = window.setInterval(function() {
      if (!state.exquisSyncEnabled || !midiOutput) {
        stopExquisLegacyKeepalive();
        return;
      }
      var now = Date.now();
      var shouldLog = now - lastExquisLegacyKeepaliveLogAt > 5000;
      if (shouldLog) lastExquisLegacyKeepaliveLogAt = now;
      sendExquisLegacyKeepalive(shouldLog ? 'Exquis legacy keepalive tick' : '');
    }, 380);
  }

  function stopExquisLegacyKeepalive() {
    if (exquisLegacyKeepaliveTimer) {
      window.clearInterval(exquisLegacyKeepaliveTimer);
      exquisLegacyKeepaliveTimer = null;
    }
  }

  function sendExquisLegacyKeyModeNow(reason, options) {
    options = options || {};
    if (!midiOutput || !midiOutput.send) return false;
    lastExquisLegacySyncAt = Date.now();
    var cells = makeGrid(1);
    var scale = getScale();
    var includeNoteMap = options.forceNoteMap || !exquisLegacyNoteMapSent;
    var lightTarget = state.legacyLightTarget || 'buttons';
    var ok = sendExquisLegacyKeepalive('');
    var noteMapCount = 0;
    var noteColorCount = 0;
    var buttonColorCount = 0;
    for (var i = 0; i < cells.length; i++) {
      var cell = cells[i];
      var padId = exquisLegacyPadId(cell);
      var color = exquisLegacyColorForCell(cell, scale);
      if (includeNoteMap) {
        ok = sendRawMidi(buildExquisLegacySysex(0x04, [padId, cell.midi]), options.verbose ? 'Exquis legacy note-map ' + cell.id + '=' + noteLabelFromMidi(cell.midi) : '') && ok;
        noteMapCount += 1;
      }
      if (lightTarget === 'notes' || lightTarget === 'both') {
        ok = sendRawMidi(buildExquisLegacySysex(0x03, [padId, color[0], color[1], color[2]]), options.verbose ? 'Exquis legacy note-color ' + cell.id : '') && ok;
        noteColorCount += 1;
      }
      if (lightTarget === 'buttons' || lightTarget === 'both') {
        ok = sendRawMidi(buildExquisLegacySysex(0x07, [padId, color[0], color[1], color[2]]), options.verbose ? 'Exquis legacy button-color ' + cell.id : '') && ok;
        buttonColorCount += 1;
      }
    }
    if (includeNoteMap) exquisLegacyNoteMapSent = true;
    state.exquisProtocol = 'legacy';
    state.exquisSyncStatus = 'Exquis sync: legacy lights sent ' + getTonicName() + ' ' + getScale().name;
    logEvent('midi', (reason || 'Exquis legacy key/mode') + ' sent buttonColors=' + buttonColorCount + ' noteColors=' + noteColorCount + ' noteMap=' + noteMapCount + ' target=' + lightTarget + ' tonic=' + getTonicName() + ' scale=' + getScale().name);
    startExquisLegacyKeepalive();
    return ok;
  }

  function sendExquisLegacyKeyMode(reason, options) {
    if (exquisLegacySyncTimer) window.clearTimeout(exquisLegacySyncTimer);
    exquisLegacySyncTimer = window.setTimeout(function() {
      exquisLegacySyncTimer = null;
      sendExquisLegacyKeyModeNow(reason, options);
      render();
    }, options && options.immediate ? 0 : 80);
    return true;
  }

  function probeExquisHardware() {
    if (!midiOutput) {
      state.exquisSyncStatus = 'Exquis probe: no MIDI output';
      logEvent('midi', 'Exquis probe unavailable: no MIDI output');
      render();
      return;
    }
    state.exquisSyncStatus = 'Exquis probe: sent diagnostic messages';
    logEvent('midi', 'Exquis probe started; watch for raw SysEx receive lines');
    sendRawMidi([0xF0, 0x7E, 0x7F, 0x06, 0x01, 0xF7], 'Exquis probe universal identity request');
    sendOfficialProbeMask(EXQUIS_DEVELOPER_LEGACY_PROBE_MASK, 'mask=0x20');
    window.setTimeout(function() { sendOfficialProbeMask(0x3F, 'mask=0x3F'); }, 160);
    window.setTimeout(function() {
      sendRawMidi([0xF0, 0x00, 0x21, 0x7E, 0xF7], 'Exquis probe legacy keepalive');
      sendRawMidi([0xF0, 0x00, 0x21, 0x7E, 0x04, 0x00, 0x3C, 0xF7], 'Exquis probe legacy note-map pad0 C4');
      sendExquisLegacyKeyMode('Exquis probe legacy key/mode', { immediate: true, forceNoteMap: true, verbose: true });
    }, 320);
    window.setTimeout(function() {
      sendRawMidi(buildExquisSysex(0x00, [0x00]), 'Exquis probe official developer-mode off');
      state.exquisSyncStatus = 'Exquis probe: complete; inspect console';
      render();
    }, 900);
    render();
  }

  function probeExquisNativeWrites() {
    if (!midiOutput) {
      state.exquisSyncStatus = 'Exquis native probe: no MIDI output';
      logEvent('midi', 'Exquis native probe unavailable: no MIDI output');
      render();
      return;
    }
    var masks = [
      { mask: EXQUIS_DEVELOPER_PADS_MASK, label: 'mask=0x01 pads' },
      { mask: EXQUIS_DEVELOPER_SETTINGS_SOUND_MASK, label: 'mask=0x10 settings' },
      { mask: EXQUIS_DEVELOPER_PADS_MASK | EXQUIS_DEVELOPER_SETTINGS_SOUND_MASK, label: 'mask=0x11 pads+settings' },
      { mask: EXQUIS_DEVELOPER_DIAL_LISTEN_MASK, label: 'mask=0x13 pads+encoders+settings' }
    ];
    state.exquisSyncStatus = 'Exquis native probe: running ' + getTonicName() + ' ' + getScale().name;
    logEvent('midi', 'Exquis native probe started root=' + getTonicName() + ' scale=' + getScale().name + '; watch hardware after each labeled mask');
    for (var i = 0; i < masks.length; i++) {
      (function(entry, delayMs) {
        window.setTimeout(function() {
          sendNativeWriteProbeMask(entry.mask, entry.label);
        }, delayMs);
      })(masks[i], i * 900);
    }
    window.setTimeout(function() {
      state.exquisSyncStatus = 'Exquis native probe: complete; inspect console';
      render();
    }, masks.length * 900 + 120);
    render();
  }

  function sendExquisRoot() {
    beginOfficialKeyModeTransaction('root=' + getTonicName());
    var ok = sendExquisSysex(0x06, [mod(state.tonicPc, 12)], 'root=' + getTonicName());
    endOfficialKeyModeTransaction('root=' + getTonicName());
    return ok;
  }

  function sendExquisScale() {
    var scaleIndex = exquisScaleNumberForScaleId(state.scaleId);
    beginOfficialKeyModeTransaction('scale=' + state.scaleId);
    var okNumber = sendExquisSysex(0x07, [scaleIndex], 'scale-index=' + scaleIndex);
    endOfficialKeyModeTransaction('scale=' + state.scaleId);
    return okNumber;
  }

  function requestExquisReadback() {
    var okRoot = sendExquisSysex(0x06, [], 'request-root-readback');
    var okScale = sendExquisSysex(0x07, [], 'request-scale-readback');
    return okRoot && okScale;
  }

  function refreshExquisDisplay(reason) {
    return sendExquisSysex(0x03, [], reason || 'refresh-display');
  }

  function syncExquisKeyModeToHardware() {
    if (!state.exquisSyncEnabled) return;
    sendExquisRoot();
    sendExquisScale();
    refreshExquisDisplay('refresh-after-sync');
    requestExquisReadback();
    sendExquisLegacyKeyMode('Exquis legacy key/mode after sync', { immediate: true });
    state.exquisSyncStatus = 'Exquis sync: sent ' + getTonicName() + ' ' + getScale().name + ' / legacy lights';
    render();
  }

  function handleExquisSysex(data) {
    var bytes = Array.prototype.slice.call(data || []);
    if (bytes.length === 5 && bytes[0] === 0xF0 && bytes[1] === 0x00 && bytes[2] === 0x21 && bytes[3] === 0x7E && bytes[4] === 0xF7) {
      state.exquisProtocol = 'legacy';
      state.exquisSyncStatus = 'Exquis sync: legacy protocol response';
      render();
      return;
    }
    logEvent('midi', 'raw SysEx receive bytes=' + bytesToHex(data));
    if (bytes.length >= 6 && bytes[0] === 0xF0 && bytes[1] === 0x7E && bytes[3] === 0x06 && bytes[4] === 0x02) {
      logEvent('midi', 'universal identity response payload=' + bytes.slice(5, -1).join(','));
      state.exquisSyncStatus = 'Exquis probe: identity response received';
      render();
      return;
    }
    var parsed = parseExquisSysex(data);
    if (!parsed) {
      logEvent('midi', 'ignored non-official Exquis SysEx message');
      return;
    }
    logEvent('midi', 'Exquis sync receive cmd=' + parsed.command.toString(16).padStart(2, '0').toUpperCase() + ' payload=' + parsed.payload.join(','));
    if (parsed.command === 0x06 && parsed.payload.length >= 1) {
      updateTonicFromHardwareRoot(parsed.payload[0], 'official SysEx');
    } else if (parsed.command === 0x07 && parsed.payload.length >= 1) {
      updateScaleFromHardwareNumber(parsed.payload[0], 'official SysEx');
    } else if (parsed.command === 0x03) {
      if (state.exquisSyncEnabled) syncExquisKeyModeToHardware();
    }
  }

  function enableExquisSync() {
    if (!midiOutput) {
      state.exquisSyncStatus = 'Exquis sync: no MIDI output';
      logEvent('midi', 'Exquis sync unavailable: no MIDI output');
      render();
      return;
    }
    state.exquisSyncEnabled = true;
    state.exquisSyncStatus = 'Exquis sync: starting';
    syncExquisKeyModeToHardware();
  }

  function disableExquisSync() {
    if (exquisLegacySyncTimer) {
      window.clearTimeout(exquisLegacySyncTimer);
      exquisLegacySyncTimer = null;
    }
    stopExquisLegacyKeepalive();
    if (state.exquisSyncEnabled && midiOutput && midiOutput.send) {
      sendExquisSysex(0x00, [0x00], 'developer-mode off');
      sendExquisLegacyKeepalive('Exquis legacy keepalive stop');
    }
    exquisLegacyNoteMapSent = false;
    state.exquisSyncEnabled = false;
    state.exquisSyncStatus = 'Exquis sync: off';
    render();
  }

  function setExquisDialListen(enabled) {
    if (!midiOutput) {
      state.exquisSyncStatus = 'Exquis dial listen: no MIDI output';
      render();
      return;
    }
    state.exquisDialListenEnabled = !!enabled;
    sendOfficialDialListenDeveloperMode(state.exquisDialListenEnabled, state.exquisDialListenEnabled ? 'dial-listen developer-mode pads+encoders+settings=0x13' : 'dial-listen developer-mode off');
    state.exquisSyncStatus = state.exquisDialListenEnabled ? 'Exquis dial listen: on (pads + encoders + settings are in Developer Mode)' : 'Exquis dial listen: off';
    logEvent('midi', state.exquisSyncStatus);
    render();
  }

  function toggleExquisDialListen() {
    setExquisDialListen(!state.exquisDialListenEnabled);
  }

  function toggleExquisSync() {
    if (state.exquisSyncEnabled) disableExquisSync();
    else enableExquisSync();
  }

  function enableMidi() {
    if (!navigator.requestMIDIAccess) {
      state.midiStatus = 'Web MIDI is not available in this browser.';
      setFeedback('Use Chrome or Edge for MIDI coaching.', 'bad');
      render();
      return;
    }
    navigator.requestMIDIAccess({ sysex: true }).then(function(access) {
      midiAccess = access;
      state.exquisSysexAvailable = true;
      midiAccess.onstatechange = function() {
        refreshMidiInputs(midiAccess);
        if (!midiInput || state.selectedMidiId) {
          connectMidiInput(chooseMidiInput(midiAccess));
        }
        connectMidiOutput(chooseMidiOutput(midiAccess));
        render();
      };
      var inputs = refreshMidiInputs(access);
      connectMidiOutput(chooseMidiOutput(access));
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
      logEvent('midi', 'sysex MIDI access failed, retrying input-only: ' + (err && err.message ? err.message : err));
      state.exquisSysexAvailable = false;
      state.exquisSyncStatus = 'Exquis sync: SysEx permission unavailable';
      navigator.requestMIDIAccess({ sysex: false }).then(function(access) {
        midiAccess = access;
        midiAccess.onstatechange = function() {
          refreshMidiInputs(midiAccess);
          if (!midiInput || state.selectedMidiId) connectMidiInput(chooseMidiInput(midiAccess));
          render();
        };
        var inputs = refreshMidiInputs(access);
        if (inputs.length) connectMidiInput(chooseMidiInput(access));
        else {
          disconnectMidiInput();
          state.midiStatus = 'No MIDI input found.';
          setFeedback('No MIDI input found. Confirm the Exquis is connected and not held by another app.', 'bad');
        }
        render();
      }).catch(function(fallbackErr) {
        state.midiStatus = 'MIDI permission denied.';
        logEvent('midi', 'permission/access failed: ' + (fallbackErr && fallbackErr.message ? fallbackErr.message : fallbackErr));
        setFeedback(fallbackErr && fallbackErr.message ? fallbackErr.message : 'MIDI permission denied.', 'bad');
        render();
      });
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
    var engines = getVisibleSoundEngines();
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
    for (i = 0; i < EXERCISES.length; i++) {
      var eo = document.createElement('option');
      eo.value = EXERCISES[i].id;
      eo.textContent = EXERCISES[i].name;
      els.exercise.appendChild(eo);
      if (els.exerciseButtons) {
        var eb = document.createElement('button');
        eb.type = 'button';
        eb.className = 'exercise-button';
        eb.dataset.value = EXERCISES[i].id;
        eb.setAttribute('data-testid', 'exercise-button-' + EXERCISES[i].id);
        eb.textContent = exerciseButtonLabel(EXERCISES[i]);
        eb.setAttribute('aria-label', EXERCISES[i].name + ': ' + EXERCISES[i].prompt);
        els.exerciseButtons.appendChild(eb);
      }
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
    var exercise = getExercise();
    var fingers = getStrategyFingers(strategy);
    var isPracticeMode = state.mode === 'practice';
    renderRootOptions(logicCells);
    if (els.tonic) els.tonic.value = String(state.tonicPc);
    if (els.scale) els.scale.value = state.scaleId;
    if (els.strategy) els.strategy.value = state.strategyId;
    if (els.hand) els.hand.value = state.hand;
    if (els.exercise) els.exercise.value = state.exerciseId;
    if (els.octave) els.octave.value = state.octaveSide;
    if (els.view) els.view.value = state.view;
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
    var currentStepIndex = state.step;
    var currentFinger = path.length ? fingers[mod(state.step, fingers.length)] : '';
    var ergonomicStep = scoreErgonomicStep(path, fingers, strategy, currentStepIndex);
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
    if (els.appShell) els.appShell.setAttribute('data-mode', state.mode);
    if (els.exquisDevice) {
      els.exquisDevice.setAttribute('data-orientation', state.orientation);
      els.exquisDevice.setAttribute('data-rotation', String(mod(state.rotation, 360)));
    }
    els.keyboard.className = 'keyboard keyboard-' + state.orientation + (state.rotation === 90 || state.rotation === 270 ? ' keyboard-rotated-sideways' : '');
    els.keyboard.setAttribute('data-mode', state.mode);
    els.keyboard.setAttribute('data-rotation', String(mod(state.rotation, 360)));
    renderEdgeControls();
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
      var displayMidi = isPracticeMode && inPath && typeof pathMidiById[cell.id] === 'number' ? pathMidiById[cell.id] : cell.midi;
      var hardwareLit = isPracticeMode && state.view === 'practice' && !!litPracticeById[cell.id];
      var inScale = state.view === 'map' ? false : (isPracticeMode && state.view === 'practice' ? inPath : isScalePc(cell.pc, scale));
      var isTonic = cell.pc === state.tonicPc;
      var isCurrent = isPracticeMode && current && current.id.replace('-octave', '') === cell.id;
      var heldInfo = getHeldInfoForCell(cell);
      var heldLevel = heldInfo.level;
      var heldPressure = heldLevel / 127;
      var key = document.createElement('button');
      var classes = ['key'];
      if (hardwareLit) classes.push('hardware-lit');
      if (inScale) classes.push('in-scale');
      if (isPracticeMode && inPath && state.view === 'practice') classes.push('in-path');
      if (isTonic) classes.push('tonic');
      if (isCurrent) classes.push('current');
      if (isPracticeMode && state.view === 'calibration' && isCurrent) classes.push('calibration-target');
      if (heldLevel > 0 && heldInfo.exact) classes.push('midi-held');
      if (state.rawMidiFlash && state.activeMidiCellId === cell.id) classes.push('midi-hit');
      if (!state.rawMidiFlash && state.lastMidiCellId === cell.id) classes.push('midi-last');
      if (state.rawMidiFlash && state.activeMidiPc === null && isCurrent) classes.push('raw-midi-hit');
      if (state.calibrated[cell.id]) classes.push('calibrated');
      if (state.mismatched[cell.id]) classes.push('mismatch');
      if (isPracticeMode && state.view === 'practice' && !inPath && !hardwareLit) classes.push('dimmed');
      if (isPracticeMode && state.view === 'scale' && !inScale) classes.push('dimmed');
      if (isPracticeMode && state.view === 'calibration' && !isCurrent) classes.push('dimmed');
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
      if (isPracticeMode && inPath && state.view === 'practice') {
        var degree = document.createElement('span');
        degree.className = 'degree-badge';
        degree.textContent = String((pathIndexById[cell.id] || 0) + 1);
        degree.setAttribute('aria-label', 'Step ' + String((pathIndexById[cell.id] || 0) + 1));
        key.appendChild(degree);
        var finger = document.createElement('span');
        finger.className = 'finger';
        finger.textContent = fingerShortName(fingerById[cell.id]);
        finger.setAttribute('aria-label', fingerDisplayName(fingerById[cell.id]));
        key.appendChild(finger);
      }
      els.keyboard.appendChild(key);
    }

    if (els.practicePathStrip) {
      clearChildren(els.practicePathStrip);
      if (isPracticeMode) {
        for (var ps = 0; ps < path.length; ps++) {
          var chip = document.createElement('span');
          chip.className = 'path-chip' + (ps === state.step ? ' active' : '');
          if (isHandShiftStep(strategy, ps)) chip.className += ' shift-chip';
          chip.setAttribute('data-testid', 'path-chip');
          chip.textContent = String(ps + 1) + ' ' + noteName(path[ps].midi) + octave(path[ps].midi);
          chip.setAttribute('aria-label', 'Step ' + String(ps + 1) + ' ' + noteName(path[ps].midi) + octave(path[ps].midi) + ' ' + fingerDisplayName(fingers[ps % fingers.length]) + (isHandShiftStep(strategy, ps) ? ' Shift hand' : ''));
          els.practicePathStrip.appendChild(chip);
        }
      }
    }
    els.title.textContent = getTonicName() + ' ' + scale.name;
    els.subtitle.textContent = isPracticeMode
      ? 'Practice: ' + (state.hand === 'right' ? 'Right' : 'Left') + ' hand: ' + strategy.name + ' / ' + exercise.name
      : 'Play: full Exquis surface / MIDI and audio live';
    if (els.handButtons) {
      var handChoiceButtons = els.handButtons.querySelectorAll('button[data-value]');
      for (var hb = 0; hb < handChoiceButtons.length; hb++) {
        var handButton = handChoiceButtons[hb];
        var handActive = handButton.dataset.value === state.hand;
        handButton.classList.toggle('active', handActive);
        handButton.setAttribute('aria-pressed', handActive ? 'true' : 'false');
      }
    }
    if (els.octaveButtons) {
      var octaveChoiceButtons = els.octaveButtons.querySelectorAll('button[data-value]');
      for (var ob = 0; ob < octaveChoiceButtons.length; ob++) {
        var octaveButton = octaveChoiceButtons[ob];
        var octaveActive = octaveButton.dataset.value === state.octaveSide;
        var octaveDisabled = state.exerciseId === 'two_octaves';
        octaveButton.classList.toggle('active', octaveActive);
        octaveButton.disabled = octaveDisabled;
        octaveButton.setAttribute('aria-pressed', octaveActive ? 'true' : 'false');
      }
    }
    if (els.exerciseButtons) {
      var exerciseChoiceButtons = els.exerciseButtons.querySelectorAll('button[data-value]');
      for (var eb = 0; eb < exerciseChoiceButtons.length; eb++) {
        var exerciseButton = exerciseChoiceButtons[eb];
        var exerciseActive = exerciseButton.dataset.value === state.exerciseId;
        exerciseButton.classList.toggle('active', exerciseActive);
        exerciseButton.setAttribute('aria-pressed', exerciseActive ? 'true' : 'false');
      }
    }
    els.fingerRule.textContent = getHandRule(strategy);
    els.drillPrompt.textContent = isPracticeMode ? exercise.prompt : 'Free-play the full Exquis surface. MIDI, pressure, audio, and note highlights stay live while scoring is paused.';
    els.stepReadout.textContent = path.length ? String(state.step + 1) + ' / ' + path.length : '0 / 0';
    els.currentNote.textContent = isPracticeMode && current ? noteName(current.midi) + octave(current.midi) : 'Free';
    els.currentDegree.textContent = isPracticeMode && current ? 'Scale degree ' + getScaleDegree(current, scale) : 'No target in play mode';
    if (els.targetFinger) els.targetFinger.textContent = isPracticeMode && current ? fingerDisplayName(currentFinger) : 'Finger --';
    if (els.targetStep) els.targetStep.textContent = isPracticeMode && current ? 'Step ' + String(state.step + 1) + ' of ' + String(path.length) : 'Step --';
    if (els.buttonReason) els.buttonReason.textContent = isPracticeMode && current ? describeButtonChoice(cells, current, rootCell) : 'Free-play chooses any physical button.';
    if (els.fingerReason) els.fingerReason.textContent = isPracticeMode && current ? describeFingerChoice(strategy, currentStepIndex, currentFinger, fingers) : 'No fingering scaffold in play mode.';
    if (els.motionReason) els.motionReason.textContent = isPracticeMode && current ? describeMotionChoice(strategy, currentStepIndex, fingers) : 'Move freely in play mode.';
    if (els.ergonomicReason) {
      els.ergonomicReason.textContent = isPracticeMode && current ? ergonomicStep.text : 'Movement load: not scored in play mode.';
      els.ergonomicReason.setAttribute('data-load-level', isPracticeMode && current ? ergonomicStep.level : 'off');
    }
    els.audioStatus.textContent = state.audioStatus;
    if (els.performanceVolume) els.performanceVolume.value = String(state.performanceVolume);
    if (els.performanceVolumeValue) els.performanceVolumeValue.textContent = String(Math.round(state.performanceVolume));
    if (els.pressureCurve) els.pressureCurve.value = state.pressureCurve;
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
    els.drillScore.textContent = isPracticeMode ? 'Score: ' + state.correctCount + ' correct / ' + state.missCount + ' missed / streak ' + state.streak : 'Play mode: score paused / all keys available';
    updateCalibrationStats();
    if (state.view === 'calibration') {
      els.assumptionText.className = 'calibration-note';
      els.assumptionText.textContent = 'Calibration preview: this will become the hardware-matching mode. Press Play to hear the target, then compare it with the matching physical Exquis button.';
    } else {
      els.assumptionText.className = '';
      els.assumptionText.textContent = 'This first build uses a documented Exquis-style model: horizontal semitones and vertical thirds. It is meant for fingering exploration, then calibration against the physical keyboard.';
    }
    if (els.exquisSyncStatus) els.exquisSyncStatus.textContent = state.exquisSyncStatus;
    if (els.syncExquis) {
      els.syncExquis.disabled = !midiAccess || !state.exquisSysexAvailable || !midiOutput;
      els.syncExquis.textContent = state.exquisSyncEnabled ? 'Stop Sync' : 'Sync Key/Mode';
      els.syncExquis.setAttribute('aria-pressed', state.exquisSyncEnabled ? 'true' : 'false');
    }
    if (els.probeExquis) {
      els.probeExquis.disabled = !midiAccess || !state.exquisSysexAvailable || !midiOutput;
    }
    if (els.nativeProbeExquis) {
      els.nativeProbeExquis.disabled = !midiAccess || !state.exquisSysexAvailable || !midiOutput;
    }
    if (els.dialListen) {
      els.dialListen.disabled = !midiAccess || !state.exquisSysexAvailable || !midiOutput;
      els.dialListen.textContent = state.exquisDialListenEnabled ? 'Stop Dial' : 'Dial Listen';
      els.dialListen.setAttribute('aria-pressed', state.exquisDialListenEnabled ? 'true' : 'false');
    }
    if (els.legacyMap) els.legacyMap.value = state.legacyMap;
    if (els.legacyLight) els.legacyLight.value = state.legacyLightTarget;
  }

  function bindEvents() {
    els.tonic.addEventListener('change', function() {
      state.tonicPc = parseInt(els.tonic.value, 10) || 0;
      state.rootCellId = '';
      state.step = 0;
      if (state.exquisSyncEnabled && Date.now() > exquisSyncSuppressUntil) {
        sendExquisRoot();
        refreshExquisDisplay('refresh-after-root');
        requestExquisReadback();
        sendExquisLegacyKeyMode('Exquis legacy key/mode after root');
        state.exquisSyncStatus = 'Exquis sync: sent ' + getTonicName() + ' ' + getScale().name;
      }
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
      if (state.exquisSyncEnabled && Date.now() > exquisSyncSuppressUntil) {
        sendExquisScale();
        refreshExquisDisplay('refresh-after-scale');
        requestExquisReadback();
        sendExquisLegacyKeyMode('Exquis legacy key/mode after scale');
        state.exquisSyncStatus = 'Exquis sync: sent ' + getTonicName() + ' ' + getScale().name;
      }
      render();
    });
    els.legacyMap.addEventListener('change', function() {
      state.legacyMap = els.legacyMap.value || 'bottom_left';
      exquisLegacyNoteMapSent = false;
      if (state.exquisSyncEnabled) sendExquisLegacyKeyMode('Exquis legacy key/mode map=' + state.legacyMap, { immediate: true, forceNoteMap: true });
      render();
    });
    els.legacyLight.addEventListener('change', function() {
      state.legacyLightTarget = els.legacyLight.value || 'buttons';
      if (state.exquisSyncEnabled) sendExquisLegacyKeyMode('Exquis legacy key/mode lights=' + state.legacyLightTarget, { immediate: true });
      render();
    });
    els.mode.addEventListener('change', function() {
      setMode(els.mode.value);
      render();
    });
    els.practiceMode.addEventListener('click', function() {
      setMode('practice');
      render();
    });
    els.playMode.addEventListener('click', function() {
      setMode('play');
      render();
    });
    if (els.handButtons) {
      els.handButtons.addEventListener('click', function(event) {
        var button = event.target.closest('button[data-value]');
        if (!button) return;
        state.hand = button.dataset.value === 'right' ? 'right' : 'left';
        els.hand.value = state.hand;
        render();
      });
    }
    if (els.octaveButtons) {
      els.octaveButtons.addEventListener('click', function(event) {
        var button = event.target.closest('button[data-value]');
        if (!button || button.disabled) return;
        state.octaveSide = button.dataset.value === 'lower' ? 'lower' : 'higher';
        state.rootCellId = '';
        state.step = 0;
        els.octave.value = state.octaveSide;
        render();
      });
    }
    els.octave.addEventListener('change', function() {
      state.octaveSide = els.octave.value === 'lower' ? 'lower' : 'higher';
      state.rootCellId = '';
      state.step = 0;
      render();
    });
    els.hand.addEventListener('change', function() {
      state.hand = els.hand.value;
      render();
    });
    if (els.exerciseButtons) {
      els.exerciseButtons.addEventListener('click', function(event) {
        var button = event.target.closest('button[data-value]');
        if (!button) return;
        state.exerciseId = button.dataset.value;
        els.exercise.value = state.exerciseId;
        state.step = 0;
        render();
      });
    }
    els.exercise.addEventListener('change', function() {
      state.exerciseId = els.exercise.value;
      state.step = 0;
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
    els.showAllEngines.addEventListener('change', function() {
      state.showAllEngines = els.showAllEngines.checked;
      invalidateSsliPresetCache();
      renderSoundSelectorOptions();
      logEvent('audio', 'show all sound engines ' + (state.showAllEngines ? 'on' : 'off'));
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
    els.performanceVolume.addEventListener('input', function() {
      state.performanceVolume = Math.max(0, Math.min(100, parseFloat(els.performanceVolume.value) || 0));
      if (els.performanceVolumeValue) els.performanceVolumeValue.textContent = String(Math.round(state.performanceVolume));
      applyPerformanceVolume();
      logEvent('audio', 'performance volume ' + Math.round(state.performanceVolume));
    });
    els.pressureCurve.addEventListener('change', function() {
      state.pressureCurve = els.pressureCurve.value;
      logEvent('audio', 'pressure curve ' + state.pressureCurve);
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
    els.syncExquis.addEventListener('click', toggleExquisSync);
    els.probeExquis.addEventListener('click', probeExquisHardware);
    els.nativeProbeExquis.addEventListener('click', probeExquisNativeWrites);
    els.dialListen.addEventListener('click', toggleExquisDialListen);
    els.audioDiag.addEventListener('click', function() {
      expandConsole();
      logSsliAudioHealth('manual');
    });
    els.resetConsole.addEventListener('click', resetConsole);
    els.copyConsole.addEventListener('click', copyConsole);
    els.exitConsole.addEventListener('click', exitConsole);
    window.addEventListener('pointerup', releaseAllUiKeys);
    window.addEventListener('blur', releaseAllUiKeys);
    window.addEventListener('resize', function() {
      render();
      if (resizeTimer) window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(function() {
        render();
      }, 40);
    });
    els.midiInputSelect.addEventListener('change', function() {
      state.selectedMidiId = els.midiInputSelect.value;
      if (midiAccess) {
        connectMidiInput(chooseMidiInput(midiAccess));
        connectMidiOutput(chooseMidiOutput(midiAccess));
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
      mode: document.getElementById('modeSelect'),
      practiceMode: document.getElementById('practiceMode'),
      playMode: document.getElementById('playMode'),
      octave: document.getElementById('octaveSelect'),
      octaveButtons: document.getElementById('octaveButtons'),
      hand: document.getElementById('handSelect'),
      handButtons: document.getElementById('handButtons'),
      exercise: document.getElementById('exerciseSelect'),
      exerciseButtons: document.getElementById('exerciseButtons'),
      strategy: document.getElementById('strategySelect'),
      view: document.getElementById('viewSelect'),
      orientation: document.getElementById('orientationSelect'),
      rotateSurface: document.getElementById('rotateSurface'),
      tone: document.getElementById('toneSelect'),
      soundEngine: document.getElementById('soundEngineSelect'),
      soundCategory: document.getElementById('soundCategorySelect'),
      soundPreset: document.getElementById('soundPresetSelect'),
      showAllEngines: document.getElementById('showAllEngines'),
      fxCategory: document.getElementById('fxCategorySelect'),
      fxPreset: document.getElementById('fxPresetSelect'),
      performanceVolume: document.getElementById('performanceVolume'),
      performanceVolumeValue: document.getElementById('performanceVolumeValue'),
      pressureCurve: document.getElementById('pressureCurveSelect'),
      filterType: document.getElementById('filterTypeSelect'),
      filterCutoff: document.getElementById('filterCutoff'),
      filterResonance: document.getElementById('filterResonance'),
      filterCutoffValue: document.getElementById('filterCutoffValue'),
      filterResonanceValue: document.getElementById('filterResonanceValue'),
      autoAdvance: document.getElementById('autoAdvance'),
      exquisDevice: document.getElementById('exquisDevice'),
      keyboard: document.getElementById('keyboard'),
      practicePathStrip: document.getElementById('practicePathStrip'),
      edgeTopControls: document.getElementById('edgeTopControls'),
      edgeBottomControls: document.getElementById('edgeBottomControls'),
      edgeControlStatus: document.getElementById('edgeControlStatus'),
      title: document.getElementById('stateTitle'),
      subtitle: document.getElementById('stateSubtitle'),
      fingerRule: document.getElementById('fingerRule'),
      targetFinger: document.getElementById('targetFinger'),
      targetStep: document.getElementById('targetStep'),
      buttonReason: document.getElementById('buttonReason'),
      fingerReason: document.getElementById('fingerReason'),
      motionReason: document.getElementById('motionReason'),
      ergonomicReason: document.getElementById('ergonomicReason'),
      drillPrompt: document.getElementById('drillPrompt'),
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
      legacyMap: document.getElementById('legacyMapSelect'),
      legacyLight: document.getElementById('legacyLightSelect'),
      enableMidi: document.getElementById('enableMidi'),
      syncExquis: document.getElementById('syncExquis'),
      probeExquis: document.getElementById('probeExquis'),
      nativeProbeExquis: document.getElementById('nativeProbeExquis'),
      dialListen: document.getElementById('dialListen'),
      exquisSyncStatus: document.getElementById('exquisSyncStatus'),
      lastMidi: document.getElementById('lastMidi'),
      coachFeedback: document.getElementById('coachFeedback'),
      drillScore: document.getElementById('drillScore'),
      calibrationStats: document.getElementById('calibrationStats'),
      clearCalibration: document.getElementById('clearCalibration'),
      consolePanel: document.getElementById('consolePanel'),
      diagnosticLog: document.getElementById('diagnosticLog'),
      audioDiag: document.getElementById('audioDiag'),
      resetConsole: document.getElementById('resetConsole'),
      copyConsole: document.getElementById('copyConsole'),
      exitConsole: document.getElementById('exitConsole')
    };
    renderOptions();
    els.appShell = document.querySelector('[data-testid="app-shell"]');
    els.tonic.value = String(state.tonicPc);
    els.mode.value = state.mode;
    setMode(state.mode);
    els.octave.value = state.octaveSide;
    els.hand.value = state.hand;
    els.exercise.value = state.exerciseId;
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
    els.performanceVolume.value = String(state.performanceVolume);
    els.pressureCurve.value = state.pressureCurve;
    els.filterType.value = state.filterType;
    els.filterCutoff.value = String(state.filterCutoff);
    els.filterResonance.value = String(state.filterResonance);
    els.showAllEngines.checked = state.showAllEngines;
    els.autoAdvance.checked = state.autoAdvance;
    bindEvents();
    ensureFreshSsliFrame();
    var ssliFrame = document.getElementById('ssliEngineFrame');
    if (ssliFrame) {
      ssliFrame.addEventListener('load', function() {
        renderSoundSelectorOptions();
        syncSoundSelectorsFromPreset();
        render();
        var host = getSsliHost();
        var readiness = host && host.SynthLab ? describeSsliReadiness(host.SynthLab, 'apply') : 'missing runtime host';
        logEvent('audio', 'SSLI runtime preset API ' + readiness);
        if (readiness === 'ready') applySelectedSsliPreset();
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
