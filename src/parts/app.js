(function() {
  'use strict';

  var SSLI_VENDOR = window.SSLI_VENDOR || {};
  var SSLI_MODES = SSLI_VENDOR.scalesModes || {};
  var SSLI_PRESETS = SSLI_VENDOR.presetLibraries || {};
  var SSLI_FX_PRESETS = SSLI_VENDOR.fxPresets || {};
  var SSLI_PROGRESSION_GROUPS = SSLI_VENDOR.progressionGroups || [];
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
      family: 'technique',
      prompt: 'Play the centered root-to-octave scale path. Keep the shape on the inner two Exquis chains.'
    },
    {
      id: 'two_octaves',
      name: 'Two octaves',
      family: 'technique',
      prompt: 'Continue the same Exquis chain shape through the second octave without switching into piano-style fingering.'
    },
    {
      id: 'inner_ladder',
      name: 'Inner-chain ladder',
      family: 'technique',
      prompt: 'Climb the inner two chains, then reverse the same physical path back to the centered root.'
    },
    {
      id: 'root_returns',
      name: 'Root returns',
      family: 'technique',
      prompt: 'Return to the centered root between every scale tone so the hand keeps its home reference.'
    },
    {
      id: 'dorian_i_iv_vamp',
      name: 'Dorian i-IV vamp',
      family: 'progressions',
      prompt: 'Alternate the Dorian minor home chord and major IV shape. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'major_i_iv_vi_v',
      name: 'Pop I-IV-vi-V',
      family: 'progressions',
      prompt: 'Move through the pop loop in order. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'major_i_iii_iv_v',
      name: 'Cadence I-iii-IV-V',
      family: 'progressions',
      prompt: 'Move from tonic through the mediant into a dominant cadence. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'major_i_ii_vi_iv',
      name: 'Pop I-ii-vi-IV',
      family: 'progressions',
      prompt: 'Move through the four-chord loop in order. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'major_circle_of_fifths',
      name: 'Circle I-IV-vii-iii-vi-ii-V-I',
      family: 'progressions',
      prompt: 'Follow the circle sequence. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'minor_i_iv_v_i',
      name: 'Minor i-iv-V-i',
      family: 'progressions',
      prompt: 'Resolve the minor cadence with a major dominant. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'minor_i_bVII_bVI_bVII',
      name: 'Minor i-bVII-bVI-bVII',
      family: 'progressions',
      prompt: 'Move through the descending minor-color loop. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'dorian_i_bVII_iv',
      name: 'Dorian i-bVII-IV',
      family: 'progressions',
      prompt: 'Move through the Dorian vamp in order. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'phrygian_i_bII_vamp',
      name: 'Phrygian i-bII vamp',
      family: 'progressions',
      prompt: 'Alternate the Phrygian minor home chord and bII shape. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'major_third',
      name: 'Major third',
      family: 'shapes',
      prompt: 'Press the root and third together as one compact interval grip.'
    },
    {
      id: 'major_triad',
      name: 'Major triad',
      family: 'shapes',
      prompt: 'Press the root, third, and fifth together as one compact grip.'
    },
    {
      id: 'harmony_triad',
      name: 'Harmony triad',
      family: 'shapes',
      prompt: 'Choose a quality and inversion, then press the highlighted chord shape together.'
    },
    {
      id: 'voice_leading',
      name: 'Voice leading',
      family: 'shapes',
      prompt: 'Play the source triad, then move only the voices needed for the closest common-tone destination.'
    },
    {
      id: 'c_major_progression',
      name: 'Major I-IV-V-I',
      family: 'progressions',
      prompt: 'Play each chord in order. Keep the pulse steady and repair the current chord before moving on.'
    },
    {
      id: 'c_major_ii_v_i',
      name: 'Major ii-V-I',
      family: 'progressions',
      prompt: 'Play each chord in order. Keep the pulse steady and repair the current chord before moving on.'
    },
    {
      id: 'major_i_v_vi_iv',
      name: 'Major I-V-vi-IV',
      family: 'progressions',
      prompt: 'Move through the pop progression in order. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'major_i_vi_ii_v',
      name: 'Major I-vi-ii-V',
      family: 'progressions',
      prompt: 'Move through the turnaround in order. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'major_12_bar_blues',
      name: 'Major 12-bar blues',
      family: 'progressions',
      prompt: 'Hold the twelve-bar form. Keep each chord together and repair the current chord before moving on.'
    },
    {
      id: 'ear_minor_third',
      name: 'Hear a minor third',
      family: 'ear',
      prompt: 'Hear the interval, then find and press the matching two-button shape together.'
    },
    {
      id: 'ear_major_third',
      name: 'Hear a major third',
      family: 'ear',
      prompt: 'Hear the interval, then find and press the matching two-button shape together.'
    },
    {
      id: 'ear_perfect_fourth',
      name: 'Hear a perfect fourth',
      family: 'ear',
      prompt: 'Hear the interval, then find and press the matching two-button shape together.'
    },
    {
      id: 'ear_perfect_fifth',
      name: 'Hear a perfect fifth',
      family: 'ear',
      prompt: 'Hear the interval, then find and press the matching two-button shape together.'
    }
  ];
  var EXERCISE_FAMILIES = [
    { id: 'technique', name: 'Technique' },
    { id: 'shapes', name: 'Shapes' },
    { id: 'progressions', name: 'Progressions' },
    { id: 'repertoire', name: 'Repertoire' },
    { id: 'ear', name: 'Ear training' }
  ];
  var HEARD_INTERVAL_FIXTURES = {
    ear_minor_third: { quality: 'minor-third', semitones: 3 },
    ear_major_third: { quality: 'major-third', semitones: 4 },
    ear_perfect_fourth: { quality: 'perfect-fourth', semitones: 5 },
    ear_perfect_fifth: { quality: 'perfect-fifth', semitones: 7 }
  };
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
  'FM::Ambient::Breathing Space': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Deep Space Hum': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Fog Horn': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Forest Canopy': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Frozen Lake': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Glass Rain': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Memory Wash': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Northern Lights': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Quantum Field': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Starfield': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Submerged': { instrumentVolume: 100, outputGain: 1 },
  'FM::Ambient::Tape Echo Pad': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bass::808 Sub FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bass::ACID BASS FM': { instrumentVolume: 46, outputGain: 1 },
  'FM::Bass::BASS 1': { instrumentVolume: 64, outputGain: 1 },
  'FM::Bass::Distortion Bass': { instrumentVolume: 61, outputGain: 1 },
  'FM::Bass::FRETLESS BASS FM': { instrumentVolume: 63, outputGain: 1 },
  'FM::Bass::FRETLESS BASS FM II': { instrumentVolume: 87, outputGain: 1 },
  'FM::Bass::Muted Bass': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bass::PICK BASS FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bass::Reese Bass': { instrumentVolume: 59, outputGain: 1 },
  'FM::Bass::SLAP BASS FM': { instrumentVolume: 50, outputGain: 1 },
  'FM::Bass::SLAP BASS FM II': { instrumentVolume: 90, outputGain: 1 },
  'FM::Bass::SUB BASS FM': { instrumentVolume: 70, outputGain: 1 },
  'FM::Bass::SYNTH BASS FM': { instrumentVolume: 57, outputGain: 1 },
  'FM::Bass::SYNTH BASS FM II': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bass::Wobble Bass': { instrumentVolume: 54, outputGain: 1 },
  'FM::Bells::CHURCH BELL': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bells::CHURCH BELL II': { instrumentVolume: 49, outputGain: 1 },
  'FM::Bells::COWBELL': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bells::GAMELAN FM': { instrumentVolume: 84, outputGain: 1 },
  'FM::Bells::KALIMBA': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bells::STEEL DRUM FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bells::STEEL DRUMS': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bells::TUBULAR BELLS': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bells::WIND CHIME': { instrumentVolume: 100, outputGain: 1 },
  'FM::Bells::WIND CHIMES': { instrumentVolume: 100, outputGain: 1 },
  'FM::Brass::BRASS 1': { instrumentVolume: 40, outputGain: 1 },
  'FM::Brass::BRASS ENSEMBLE FM': { instrumentVolume: 70, outputGain: 1 },
  'FM::Brass::SYNTH BRASS FM': { instrumentVolume: 49, outputGain: 1 },
  'FM::Brass::Synth BRASS SECTION FM': { instrumentVolume: 94, outputGain: 1 },
  'FM::Brass::Synth FRENCH HORN FM': { instrumentVolume: 46, outputGain: 1 },
  'FM::Brass::Synth FRENCH HORN FM II': { instrumentVolume: 57, outputGain: 1 },
  'FM::Brass::Synth TROMBONE FM': { instrumentVolume: 62, outputGain: 1 },
  'FM::Brass::Synth TROMBONE FM II': { instrumentVolume: 84, outputGain: 1 },
  'FM::Brass::Synth TRUMPET FM': { instrumentVolume: 52, outputGain: 1 },
  'FM::Brass::Synth TRUMPET FM II': { instrumentVolume: 100, outputGain: 1 },
  'FM::Choir/Vocal::Angel Choir': { instrumentVolume: 100, outputGain: 1 },
  'FM::Choir/Vocal::Dark Chant': { instrumentVolume: 100, outputGain: 1 },
  'FM::Choir/Vocal::Ethereal Voices': { instrumentVolume: 100, outputGain: 1 },
  'FM::Choir/Vocal::Robot Voice': { instrumentVolume: 66, outputGain: 1 },
  'FM::Choir/Vocal::Soprano Solo': { instrumentVolume: 100, outputGain: 1 },
  'FM::Choir/Vocal::Vocal Formant Ah': { instrumentVolume: 100, outputGain: 1 },
  'FM::Choir/Vocal::Vocal Formant Ooh': { instrumentVolume: 100, outputGain: 1 },
  'FM::Choir/Vocal::Vox Humana': { instrumentVolume: 72, outputGain: 1 },
  'FM::Cinematic::Choir of Ghosts': { instrumentVolume: 100, outputGain: 1 },
  'FM::Cinematic::Cosmic Dawn': { instrumentVolume: 90, outputGain: 1 },
  'FM::Cinematic::Danger Zone': { instrumentVolume: 50, outputGain: 1 },
  'FM::Cinematic::Distant Horizon': { instrumentVolume: 87, outputGain: 1 },
  'FM::Cinematic::Epic Brass Stab': { instrumentVolume: 84, outputGain: 1 },
  'FM::Cinematic::Heartbeat Sub': { instrumentVolume: 100, outputGain: 1 },
  'FM::Cinematic::Impact Boom': { instrumentVolume: 100, outputGain: 1 },
  'FM::Cinematic::Neon City': { instrumentVolume: 61, outputGain: 1 },
  'FM::Cinematic::Sci-Fi Scanner': { instrumentVolume: 57, outputGain: 1 },
  'FM::Cinematic::Tension Pulse': { instrumentVolume: 100, outputGain: 1 },
  'FM::Cinematic::Underscore Drone': { instrumentVolume: 100, outputGain: 1 },
  'FM::Cinematic::War Drums FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::FX::EXPLOSION FM': { instrumentVolume: 59, outputGain: 1 },
  'FM::FX::INIT FM': { instrumentVolume: 57, outputGain: 1 },
  'FM::FX::LASER': { instrumentVolume: 46, outputGain: 1 },
  'FM::FX::LASER FM': { instrumentVolume: 56, outputGain: 1 },
  'FM::FX::METALLIC HIT': { instrumentVolume: 76, outputGain: 1 },
  'FM::FX::SIREN FM': { instrumentVolume: 57, outputGain: 1 },
  'FM::FX::SITAR FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::FX::SPACE EFFECT': { instrumentVolume: 74, outputGain: 1 },
  'FM::FX::SPACE FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::FX::WOBBLE FM': { instrumentVolume: 57, outputGain: 1 },
  'FM::Guitar::12-STRING GUITAR': { instrumentVolume: 100, outputGain: 1 },
  'FM::Guitar::CLEAN ELECTRIC': { instrumentVolume: 100, outputGain: 1 },
  'FM::Guitar::DISTORTED GUITAR': { instrumentVolume: 80, outputGain: 1 },
  'FM::Guitar::MUTED GUITAR': { instrumentVolume: 98, outputGain: 1 },
  'FM::Guitar::STEEL GUITAR': { instrumentVolume: 100, outputGain: 1 },
  'FM::Guitar::Synth ACOUSTIC GUITAR': { instrumentVolume: 96, outputGain: 1 },
  'FM::Industrial::Circuit Bent': { instrumentVolume: 71, outputGain: 1 },
  'FM::Industrial::Drill Press': { instrumentVolume: 63, outputGain: 1 },
  'FM::Industrial::Factory Floor': { instrumentVolume: 93, outputGain: 1 },
  'FM::Industrial::Metal Grind': { instrumentVolume: 59, outputGain: 1 },
  'FM::Industrial::Pneumatic Hit': { instrumentVolume: 97, outputGain: 1 },
  'FM::Industrial::Power Surge': { instrumentVolume: 59, outputGain: 1 },
  'FM::Industrial::Rust': { instrumentVolume: 88, outputGain: 1 },
  'FM::Industrial::Voltage Drop': { instrumentVolume: 74, outputGain: 1 },
  'FM::Keys::CELESTA': { instrumentVolume: 87, outputGain: 1 },
  'FM::Keys::CELESTA FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Keys::CLAVINET': { instrumentVolume: 100, outputGain: 1 },
  'FM::Keys::CLAVINET FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Keys::DX RHODES': { instrumentVolume: 69, outputGain: 1 },
  'FM::Keys::E.PIANO 1': { instrumentVolume: 50, outputGain: 1 },
  'FM::Keys::E.PIANO 2': { instrumentVolume: 71, outputGain: 1 },
  'FM::Keys::GLOCKENSPIEL': { instrumentVolume: 100, outputGain: 1 },
  'FM::Keys::HARPSICHORD': { instrumentVolume: 86, outputGain: 1 },
  'FM::Keys::HARPSICHORD FM': { instrumentVolume: 85, outputGain: 1 },
  'FM::Keys::MARIMBA': { instrumentVolume: 100, outputGain: 1 },
  'FM::Keys::MUSIC BOX': { instrumentVolume: 100, outputGain: 1 },
  'FM::Keys::MUSIC BOX FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Keys::TINE PIANO': { instrumentVolume: 53, outputGain: 1 },
  'FM::Keys::TOY PIANO FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Keys::VIBRAPHONE': { instrumentVolume: 71, outputGain: 1 },
  'FM::Keys::WURLITZER FM': { instrumentVolume: 44, outputGain: 1 },
  'FM::Keys::XYLOPHONE': { instrumentVolume: 83, outputGain: 1 },
  'FM::Leads::DIGITAL LEAD': { instrumentVolume: 40, outputGain: 1 },
  'FM::Leads::Laser Lead': { instrumentVolume: 64, outputGain: 1 },
  'FM::Leads::PORTAMENTO FM': { instrumentVolume: 54, outputGain: 1 },
  'FM::Leads::PORTAMENTO LEAD FM': { instrumentVolume: 55, outputGain: 1 },
  'FM::Leads::Portamento Lead': { instrumentVolume: 63, outputGain: 1 },
  'FM::Leads::SAW LEAD FM': { instrumentVolume: 64, outputGain: 1 },
  'FM::Leads::SCREAMER FM': { instrumentVolume: 63, outputGain: 1 },
  'FM::Leads::SQUARE LEAD FM': { instrumentVolume: 58, outputGain: 1 },
  'FM::Leads::SYN-LEAD': { instrumentVolume: 39, outputGain: 1 },
  'FM::Leads::Screaming Lead': { instrumentVolume: 55, outputGain: 1 },
  'FM::Leads::Singing Lead': { instrumentVolume: 63, outputGain: 1 },
  'FM::Leads::Sync Lead FM': { instrumentVolume: 65, outputGain: 1 },
  'FM::Leads::TRANCE FM': { instrumentVolume: 99, outputGain: 1 },
  'FM::Leads::WHISTLE FM': { instrumentVolume: 64, outputGain: 1 },
  'FM::Leads::WHISTLE LEAD': { instrumentVolume: 71, outputGain: 1 },
  'FM::Modern::FM CHIPTUNE': { instrumentVolume: 44, outputGain: 1 },
  'FM::Modern::FM DIGITAL PAD': { instrumentVolume: 76, outputGain: 1 },
  'FM::Modern::FM DROP': { instrumentVolume: 100, outputGain: 1 },
  'FM::Modern::FM GLITCH': { instrumentVolume: 76, outputGain: 1 },
  'FM::Modern::FM PLUCK': { instrumentVolume: 100, outputGain: 1 },
  'FM::Modern::FM RISER': { instrumentVolume: 66, outputGain: 1 },
  'FM::Modern::FM STAB': { instrumentVolume: 58, outputGain: 1 },
  'FM::Modern::FM WOBBLE': { instrumentVolume: 100, outputGain: 1 },
  'FM::Organ::FARFISA FM': { instrumentVolume: 55, outputGain: 1 },
  'FM::Organ::GOSPEL ORGAN FM': { instrumentVolume: 73, outputGain: 1 },
  'FM::Organ::JAZZ ORGAN FM': { instrumentVolume: 60, outputGain: 1 },
  'FM::Organ::JAZZ ORGAN FM II': { instrumentVolume: 75, outputGain: 1 },
  'FM::Organ::ORGAN 1': { instrumentVolume: 57, outputGain: 1 },
  'FM::Organ::PIPE ORGAN FM': { instrumentVolume: 55, outputGain: 1 },
  'FM::Organ::PIPE ORGAN FM II': { instrumentVolume: 55, outputGain: 1 },
  'FM::Organ::ROCK ORGAN FM': { instrumentVolume: 51, outputGain: 1 },
  'FM::Organ::ROCK ORGAN FM II': { instrumentVolume: 56, outputGain: 1 },
  'FM::Organ::Synth HARMONICA FM': { instrumentVolume: 68, outputGain: 1 },
  'FM::Pads::ATMOSPHERE FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Pads::Analog Warmth': { instrumentVolume: 100, outputGain: 1 },
  'FM::Pads::CHOIR FM': { instrumentVolume: 81, outputGain: 1 },
  'FM::Pads::CHOIR FM PAD': { instrumentVolume: 59, outputGain: 1 },
  'FM::Pads::Choir Pad FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Pads::DARK FM PAD': { instrumentVolume: 88, outputGain: 1 },
  'FM::Pads::Dark Matter': { instrumentVolume: 100, outputGain: 1 },
  'FM::Pads::EVOLVING PAD FM': { instrumentVolume: 75, outputGain: 1 },
  'FM::Pads::GLASS FM PAD': { instrumentVolume: 75, outputGain: 1 },
  'FM::Pads::GLASS PAD FM': { instrumentVolume: 91, outputGain: 1 },
  'FM::Pads::Glass Pad': { instrumentVolume: 100, outputGain: 1 },
  'FM::Pads::Metallic Shimmer': { instrumentVolume: 100, outputGain: 1 },
  'FM::Pads::SHIMMER PAD FM': { instrumentVolume: 95, outputGain: 1 },
  'FM::Pads::WARM FM PAD': { instrumentVolume: 70, outputGain: 1 },
  'FM::Pads::WARM PAD FM': { instrumentVolume: 76, outputGain: 1 },
  'FM::Percussion::FM CLAP': { instrumentVolume: 47, outputGain: 1 },
  'FM::Percussion::FM CONGA': { instrumentVolume: 71, outputGain: 1 },
  'FM::Percussion::FM COWBELL': { instrumentVolume: 62, outputGain: 1 },
  'FM::Percussion::FM SNARE': { instrumentVolume: 48, outputGain: 1 },
  'FM::Percussion::FM TOM': { instrumentVolume: 76, outputGain: 1 },
  'FM::Percussion::FM TYMPANI': { instrumentVolume: 95, outputGain: 1 },
  'FM::Strings::CONTRABASS FM': { instrumentVolume: 62, outputGain: 1 },
  'FM::Strings::ENSEMBLE FM': { instrumentVolume: 70, outputGain: 1 },
  'FM::Strings::STRINGS FM': { instrumentVolume: 65, outputGain: 1 },
  'FM::Strings::Synth CELLO FM': { instrumentVolume: 45, outputGain: 1 },
  'FM::Strings::Synth HARP FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Strings::Synth PIZZICATO FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Strings::Synth PIZZICATO FM II': { instrumentVolume: 100, outputGain: 1 },
  'FM::Strings::Synth SOLO CELLO FM': { instrumentVolume: 68, outputGain: 1 },
  'FM::Strings::Synth SOLO VIOLIN FM': { instrumentVolume: 59, outputGain: 1 },
  'FM::Strings::Synth VIOLIN FM': { instrumentVolume: 65, outputGain: 1 },
  'FM::Synth Pop::Depeche Bass': { instrumentVolume: 98, outputGain: 1 },
  'FM::Synth Pop::Electro Funk Bass': { instrumentVolume: 74, outputGain: 1 },
  'FM::Synth Pop::FM Choir Pad': { instrumentVolume: 100, outputGain: 1 },
  'FM::Synth Pop::Glassy Keys': { instrumentVolume: 96, outputGain: 1 },
  'FM::Synth Pop::Neon Arp': { instrumentVolume: 88, outputGain: 1 },
  'FM::Synth Pop::Pluck Synth': { instrumentVolume: 100, outputGain: 1 },
  'FM::Synth Pop::Pop Pad': { instrumentVolume: 100, outputGain: 1 },
  'FM::Synth Pop::Retro Stab': { instrumentVolume: 100, outputGain: 1 },
  'FM::Synth Pop::Synthwave Lead': { instrumentVolume: 57, outputGain: 1 },
  'FM::Synth Pop::Talk Box FM': { instrumentVolume: 73, outputGain: 1 },
  'FM::Vintage::70s FM Brass': { instrumentVolume: 72, outputGain: 1 },
  'FM::Vintage::80s Slap Bass': { instrumentVolume: 68, outputGain: 1 },
  'FM::Vintage::Crystal EP': { instrumentVolume: 100, outputGain: 1 },
  'FM::Vintage::DX Rhodes': { instrumentVolume: 66, outputGain: 1 },
  'FM::Vintage::FM Wurlitzer': { instrumentVolume: 58, outputGain: 1 },
  'FM::Vintage::Poly-5 FM': { instrumentVolume: 68, outputGain: 1 },
  'FM::Vintage::Retro Tine Piano': { instrumentVolume: 66, outputGain: 1 },
  'FM::Vintage::Synth Analog Strings FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::Vintage::Vintage Clav': { instrumentVolume: 100, outputGain: 1 },
  'FM::Vintage::Vinyl Organ': { instrumentVolume: 62, outputGain: 1 },
  'FM::Woodwinds::Synth FM BASSOON': { instrumentVolume: 69, outputGain: 1 },
  'FM::Woodwinds::Synth FM CLARINET': { instrumentVolume: 100, outputGain: 1 },
  'FM::Woodwinds::Synth FM FLUTE': { instrumentVolume: 56, outputGain: 1 },
  'FM::Woodwinds::Synth FM OBOE': { instrumentVolume: 100, outputGain: 1 },
  'FM::Woodwinds::Synth FM PICCOLO': { instrumentVolume: 95, outputGain: 1 },
  'FM::Woodwinds::Synth FM SAXOPHONE': { instrumentVolume: 62, outputGain: 1 },
  'FM::World::Balafon FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::World::Erhu FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::World::Gamelan Bell': { instrumentVolume: 100, outputGain: 1 },
  'FM::World::Kalimba FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::World::Oud FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::World::Sitar FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::World::Steel Drum FM': { instrumentVolume: 90, outputGain: 1 },
  'FM::World::Synth Didgeridoo FM': { instrumentVolume: 100, outputGain: 1 },
  'FM::World::Synth Shakuhachi FM': { instrumentVolume: 88, outputGain: 1 },
  'FM::World::Tabla FM': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Ambient/Texture::Aeolian Harp': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Ambient/Texture::Breath Pad': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Ambient/Texture::Crystal Shimmer': { instrumentVolume: 77, outputGain: 1 },
  'Physical::Ambient/Texture::Deep Ocean Hum': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Ambient/Texture::Frozen Strings': { instrumentVolume: 83, outputGain: 1 },
  'Physical::Ambient/Texture::Glass Forest': { instrumentVolume: 85, outputGain: 1 },
  'Physical::Ambient/Texture::Rain on Metal': { instrumentVolume: 76, outputGain: 1 },
  'Physical::Ambient/Texture::Wind Through Reeds': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Accordion': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Bagpipe Drone': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Bansuri': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Bassoon': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Blown Jug': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Bottle Blow': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Clarinet': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Concert Flute': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Didgeridoo': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Harmonica': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Oboe': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Ocarina': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Pan Pipe': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Piccolo': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Quena': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Recorder': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Shakuhachi': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Blown::Tin Whistle': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Bowed::Bowed Glass': { instrumentVolume: 75, outputGain: 1 },
  'Physical::Bowed::Cello': { instrumentVolume: 65, outputGain: 1 },
  'Physical::Bowed::Cello Sul Tasto': { instrumentVolume: 72, outputGain: 1 },
  'Physical::Bowed::Contrabass': { instrumentVolume: 64, outputGain: 1 },
  'Physical::Bowed::Erhu': { instrumentVolume: 60, outputGain: 1 },
  'Physical::Bowed::Fiddle': { instrumentVolume: 64, outputGain: 1 },
  'Physical::Bowed::Hurdy Gurdy': { instrumentVolume: 61, outputGain: 1 },
  'Physical::Bowed::Morin Khuur': { instrumentVolume: 63, outputGain: 1 },
  'Physical::Bowed::Nyckelharpa': { instrumentVolume: 69, outputGain: 1 },
  'Physical::Bowed::Rebab': { instrumentVolume: 63, outputGain: 1 },
  'Physical::Bowed::Sarangi': { instrumentVolume: 59, outputGain: 1 },
  'Physical::Bowed::String Ensemble': { instrumentVolume: 71, outputGain: 1 },
  'Physical::Bowed::Viola': { instrumentVolume: 72, outputGain: 1 },
  'Physical::Bowed::Violin': { instrumentVolume: 69, outputGain: 1 },
  'Physical::Cinematic::Distant Thunder Drum': { instrumentVolume: 85, outputGain: 1 },
  'Physical::Cinematic::Horror Strings': { instrumentVolume: 53, outputGain: 1 },
  'Physical::Cinematic::Impact Metal': { instrumentVolume: 96, outputGain: 1 },
  'Physical::Cinematic::Spectral Choir': { instrumentVolume: 74, outputGain: 1 },
  'Physical::Cinematic::Tension Riser': { instrumentVolume: 52, outputGain: 1 },
  'Physical::Cinematic::Whale Song': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Ethnic::Berimbau': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Ethnic::Dizi': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Ethnic::Duduk': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Ethnic::Gamelan Metallophone': { instrumentVolume: 86, outputGain: 1 },
  'Physical::Ethnic::Kamancheh': { instrumentVolume: 65, outputGain: 1 },
  'Physical::Ethnic::Kora': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Ethnic::Mbira': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Ethnic::Santur': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Experimental::Bowed Metal': { instrumentVolume: 56, outputGain: 1 },
  'Physical::Experimental::Bowed Plate': { instrumentVolume: 53, outputGain: 1 },
  'Physical::Experimental::Bowed Saw': { instrumentVolume: 73, outputGain: 1 },
  'Physical::Experimental::Feedback Resonator': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Experimental::Metallic Drone': { instrumentVolume: 55, outputGain: 1 },
  'Physical::Experimental::Prepared Piano': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Experimental::Resonant Body': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Experimental::Struck Ice': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Experimental::Struck Springs': { instrumentVolume: 76, outputGain: 1 },
  'Physical::Experimental::Struck String': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Experimental::Wind Chime': { instrumentVolume: 76, outputGain: 1 },
  'Physical::Experimental::Wire Zither': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Hybrid::Blown Metal': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Hybrid::Bowed Bass Pluck': { instrumentVolume: 61, outputGain: 1 },
  'Physical::Hybrid::Glass Marimba': { instrumentVolume: 82, outputGain: 1 },
  'Physical::Hybrid::Plucked Membrane': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Hybrid::Struck Breath': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Banjo': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Bass Guitar': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Concert Harp': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Dulcimer': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Electric Guitar Clean': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Guzheng': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Harpsichord': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Kalimba': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Koto': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Lute': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Mandolin': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Music Box': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Nylon Guitar': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Oud': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Pizzicato': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Sitar': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Steel Guitar': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Ukulele': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Plucked::Zither': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Struck::Agogo Bells': { instrumentVolume: 89, outputGain: 1 },
  'Physical::Struck::Balafon': { instrumentVolume: 81, outputGain: 1 },
  'Physical::Struck::Church Bell': { instrumentVolume: 100, outputGain: 1 },
  'Physical::Struck::Cowbell': { instrumentVolume: 90, outputGain: 1 },
  'Physical::Struck::Crotales': { instrumentVolume: 81, outputGain: 1 },
  'Physical::Struck::Djembe': { instrumentVolume: 88, outputGain: 1 },
  'Physical::Struck::Frame Drum': { instrumentVolume: 81, outputGain: 1 },
  'Physical::Struck::Glass Chime': { instrumentVolume: 85, outputGain: 1 },
  'Physical::Struck::Glockenspiel': { instrumentVolume: 83, outputGain: 1 },
  'Physical::Struck::Gong': { instrumentVolume: 82, outputGain: 1 },
  'Physical::Struck::Hang Drum': { instrumentVolume: 83, outputGain: 1 },
  'Physical::Struck::Marimba': { instrumentVolume: 80, outputGain: 1 },
  'Physical::Struck::Singing Bowl': { instrumentVolume: 86, outputGain: 1 },
  'Physical::Struck::Steel Drum': { instrumentVolume: 84, outputGain: 1 },
  'Physical::Struck::Tabla': { instrumentVolume: 88, outputGain: 1 },
  'Physical::Struck::Temple Block': { instrumentVolume: 84, outputGain: 1 },
  'Physical::Struck::Timpani': { instrumentVolume: 87, outputGain: 1 },
  'Physical::Struck::Tubular Bells': { instrumentVolume: 96, outputGain: 1 },
  'Physical::Struck::Vibraphone': { instrumentVolume: 81, outputGain: 1 },
  'Physical::Struck::Wood Block': { instrumentVolume: 92, outputGain: 1 },
  'Physical::Struck::Xylophone': { instrumentVolume: 87, outputGain: 1 },
  'Subtractive::Ambient::Coral Reef': { instrumentVolume: 89, outputGain: 1 },
  'Subtractive::Ambient::Crystal Cave': { instrumentVolume: 82, outputGain: 1 },
  'Subtractive::Ambient::Deep Space': { instrumentVolume: 94, outputGain: 1 },
  'Subtractive::Ambient::First Light': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Ambient::Forest Whisper': { instrumentVolume: 98, outputGain: 1 },
  'Subtractive::Ambient::Ghost Choir': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Ambient::Midnight Rain': { instrumentVolume: 89, outputGain: 1 },
  'Subtractive::Ambient::Monastery': { instrumentVolume: 75, outputGain: 1 },
  'Subtractive::Ambient::Nebula Cloud': { instrumentVolume: 96, outputGain: 1 },
  'Subtractive::Ambient::Northern Lights': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Ambient::Rainfall': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Ambient::Solar Wind': { instrumentVolume: 81, outputGain: 1 },
  'Subtractive::Ambient::Tidal Drone': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Ambient::Tidal Drone II': { instrumentVolume: 83, outputGain: 1 },
  'Subtractive::Ambient::Twilight Zone': { instrumentVolume: 66, outputGain: 1 },
  'Subtractive::Analog Classics::ARP Odyssey Sweep': { instrumentVolume: 64, outputGain: 1 },
  'Subtractive::Analog Classics::Acid Squelch': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Analog Classics::Chorus Poly Pad': { instrumentVolume: 96, outputGain: 1 },
  'Subtractive::Analog Classics::Korg Mono Lead': { instrumentVolume: 68, outputGain: 1 },
  'Subtractive::Analog Classics::MS-20 Growl': { instrumentVolume: 80, outputGain: 1 },
  'Subtractive::Analog Classics::Minimoog Bass': { instrumentVolume: 91, outputGain: 1 },
  'Subtractive::Analog Classics::Model D Funk': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Analog Classics::OB-Xa Strings': { instrumentVolume: 73, outputGain: 1 },
  'Subtractive::Analog Classics::Poly Analog Ensemble': { instrumentVolume: 83, outputGain: 1 },
  'Subtractive::Analog Classics::Poly-5 Synth': { instrumentVolume: 85, outputGain: 1 },
  'Subtractive::Analog Classics::SH-101 Lead': { instrumentVolume: 92, outputGain: 1 },
  'Subtractive::Analog Classics::Steiner Filter Stab': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Analog Classics::Vintage Brass': { instrumentVolume: 68, outputGain: 1 },
  'Subtractive::Analog Classics::Warm Poly Pad': { instrumentVolume: 81, outputGain: 1 },
  'Subtractive::Analog Classics::Wasp Synth': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::808 Sine Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Acid Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Analog Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Analog Growl': { instrumentVolume: 69, outputGain: 1 },
  'Subtractive::Bass::Distorted Bass': { instrumentVolume: 28, outputGain: 1 },
  'Subtractive::Bass::FM Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::FM Pluck Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Finger Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Fingered Bass': { instrumentVolume: 95, outputGain: 1 },
  'Subtractive::Bass::Hoover Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Neuro Bass': { instrumentVolume: 28, outputGain: 1 },
  'Subtractive::Bass::Pluck Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Reese Bass': { instrumentVolume: 90, outputGain: 1 },
  'Subtractive::Bass::Reese Bass II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Rubber Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Slap Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Sub Bass': { instrumentVolume: 61, outputGain: 1 },
  'Subtractive::Bass::Sub Wobble': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Bass::Tape Bass': { instrumentVolume: 92, outputGain: 1 },
  'Subtractive::Bass::Wobble Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Brass::Flugelhorn': { instrumentVolume: 76, outputGain: 1 },
  'Subtractive::Brass::Oberheim Brass': { instrumentVolume: 76, outputGain: 1 },
  'Subtractive::Brass::Synth Brass (OB-Xa Style)': { instrumentVolume: 86, outputGain: 1 },
  'Subtractive::Brass::Synth Brass Section': { instrumentVolume: 83, outputGain: 1 },
  'Subtractive::Brass::Synth Brass Section II': { instrumentVolume: 82, outputGain: 1 },
  'Subtractive::Brass::Synth Brass Stab': { instrumentVolume: 93, outputGain: 1 },
  'Subtractive::Brass::Synth French Horn': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Brass::Synth French Horn II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Brass::Synth Muted Trumpet': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Brass::Synth Muted Trumpet II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Brass::Synth Trombone': { instrumentVolume: 82, outputGain: 1 },
  'Subtractive::Brass::Synth Trumpet': { instrumentVolume: 89, outputGain: 1 },
  'Subtractive::Brass::Synth Tuba': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Chip/Retro::8-Bit Square Lead': { instrumentVolume: 63, outputGain: 1 },
  'Subtractive::Chip/Retro::Bit Crush Lead': { instrumentVolume: 28, outputGain: 1 },
  'Subtractive::Chip/Retro::Chip Arp': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Chip/Retro::Chip Noise': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Chip/Retro::Coin Collect': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Chip/Retro::Game Over': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Chip/Retro::NES Triangle Bass': { instrumentVolume: 84, outputGain: 1 },
  'Subtractive::Chip/Retro::Power Up': { instrumentVolume: 87, outputGain: 1 },
  'Subtractive::Chip/Retro::Retro Pad': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Chip/Retro::SID Bass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Cinematic::Alien Texture': { instrumentVolume: 35, outputGain: 1 },
  'Subtractive::Cinematic::Cinematic Stab': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Cinematic::Dark Drone': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Cinematic::Epic Brass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Cinematic::Foghorn': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Cinematic::Horror Pad': { instrumentVolume: 30, outputGain: 1 },
  'Subtractive::Cinematic::Impact Hit': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Cinematic::Metallic Riser': { instrumentVolume: 34, outputGain: 1 },
  'Subtractive::Cinematic::Riser': { instrumentVolume: 77, outputGain: 1 },
  'Subtractive::Cinematic::Suspense Pulse': { instrumentVolume: 75, outputGain: 1 },
  'Subtractive::Cinematic::Tension Builder': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Cinematic::Vast Space': { instrumentVolume: 89, outputGain: 1 },
  'Subtractive::Drums::Analog Kick': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Drums::Clap': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Drums::Clap II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Drums::Cowbell': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Drums::Hi-Hat Closed': { instrumentVolume: 65, outputGain: 1 },
  'Subtractive::Drums::Hi-Hat Closed II': { instrumentVolume: 51, outputGain: 1 },
  'Subtractive::Drums::Hi-Hat Open': { instrumentVolume: 64, outputGain: 1 },
  'Subtractive::Drums::Kick Drum': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Drums::Snare Crack': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Drums::Snare Drum': { instrumentVolume: 88, outputGain: 1 },
  'Subtractive::Drums::Tom': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Drums::Tom II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::EDM::Big Room Synth': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::EDM::Complextro Lead': { instrumentVolume: 89, outputGain: 1 },
  'Subtractive::EDM::Dubstep Wobble': { instrumentVolume: 29, outputGain: 1 },
  'Subtractive::EDM::Electro Stab': { instrumentVolume: 98, outputGain: 1 },
  'Subtractive::EDM::Festival Pluck': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::EDM::Future Bass Chord': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::EDM::Hardstyle Lead': { instrumentVolume: 28, outputGain: 1 },
  'Subtractive::EDM::Progressive Pad': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::EDM::Riddim Bass': { instrumentVolume: 29, outputGain: 1 },
  'Subtractive::EDM::Sidechain Pad': { instrumentVolume: 87, outputGain: 1 },
  'Subtractive::EDM::Supersaw Lead': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::EDM::Trance Pluck': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Filter Sweep': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Impact': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Laser Zap': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Metallic Hit': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Noise Burst': { instrumentVolume: 74, outputGain: 1 },
  'Subtractive::FX::Riser': { instrumentVolume: 24, outputGain: 1 },
  'Subtractive::FX::Robot Voice': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Sci-Fi Blip': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Sci-Fi Zap': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Siren': { instrumentVolume: 69, outputGain: 1 },
  'Subtractive::FX::Thunder': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Underwater': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::White Noise Sweep': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Wind': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::FX::Wind II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Celesta': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Celesta II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Clavinet': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Clavinet II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Electric Piano (Rhodes)': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Harpsichord': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Harpsichord II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Honky Tonk': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Marimba Keys': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Soft EP': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Toy Piano': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Toy Piano II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Keys::Wurli Keys': { instrumentVolume: 99, outputGain: 1 },
  'Subtractive::Keys::Wurlitzer EP': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Leads::Buzz Lead': { instrumentVolume: 56, outputGain: 1 },
  'Subtractive::Leads::Detuned Lead': { instrumentVolume: 81, outputGain: 1 },
  'Subtractive::Leads::Detuned Stack': { instrumentVolume: 68, outputGain: 1 },
  'Subtractive::Leads::Distorted Lead': { instrumentVolume: 29, outputGain: 1 },
  'Subtractive::Leads::Funky Lead': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Leads::Nasal Lead': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Leads::Octave Lead': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Leads::PWM Lead': { instrumentVolume: 90, outputGain: 1 },
  'Subtractive::Leads::Portamento Lead': { instrumentVolume: 91, outputGain: 1 },
  'Subtractive::Leads::Portamento Lead II': { instrumentVolume: 97, outputGain: 1 },
  'Subtractive::Leads::Saw Lead': { instrumentVolume: 82, outputGain: 1 },
  'Subtractive::Leads::Screamer Lead': { instrumentVolume: 28, outputGain: 1 },
  'Subtractive::Leads::Screamer Lead II': { instrumentVolume: 28, outputGain: 1 },
  'Subtractive::Leads::Square Lead': { instrumentVolume: 78, outputGain: 1 },
  'Subtractive::Leads::Sync Lead': { instrumentVolume: 45, outputGain: 1 },
  'Subtractive::Leads::Sync Lead II': { instrumentVolume: 71, outputGain: 1 },
  'Subtractive::Leads::Talk Lead': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Leads::Trance Lead': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Leads::Whistle Lead': { instrumentVolume: 71, outputGain: 1 },
  'Subtractive::Leads::Whistle Lead II': { instrumentVolume: 69, outputGain: 1 },
  'Subtractive::Lofi::Bedroom Guitar': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Lofi::Cassette Lead': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Lofi::Dusty Keys': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Lofi::Dusty Rhodes': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Lofi::Lofi Sub': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Lofi::Rain Piano': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Lofi::Tape EP': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Lofi::VHS Strings': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Lofi::Vinyl Pad': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Lofi::Worn Organ': { instrumentVolume: 74, outputGain: 1 },
  'Subtractive::Misc::Acid Square': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Misc::Arp 2600 Lead': { instrumentVolume: 74, outputGain: 1 },
  'Subtractive::Misc::Banjo': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Misc::Glockenspiel': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Misc::Korg Poly Lead': { instrumentVolume: 86, outputGain: 1 },
  'Subtractive::Misc::MS-20 Growl': { instrumentVolume: 28, outputGain: 1 },
  'Subtractive::Misc::Music Box': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Misc::Poly-5 Pad': { instrumentVolume: 90, outputGain: 1 },
  'Subtractive::Misc::Recorder': { instrumentVolume: 68, outputGain: 1 },
  'Subtractive::Misc::Sitar': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Misc::Steiner Filter Sweep': { instrumentVolume: 67, outputGain: 1 },
  'Subtractive::Misc::Synth Bagpipes': { instrumentVolume: 58, outputGain: 1 },
  'Subtractive::Misc::Synth Didgeridoo': { instrumentVolume: 72, outputGain: 1 },
  'Subtractive::Misc::Synth Harmonica': { instrumentVolume: 64, outputGain: 1 },
  'Subtractive::Misc::Synth Tuba': { instrumentVolume: 75, outputGain: 1 },
  'Subtractive::Misc::Telephone': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Misc::Telephone Ring': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Misc::Vibraphone': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Misc::Xylophone': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Noise/Industrial::Concrete': { instrumentVolume: 29, outputGain: 1 },
  'Subtractive::Noise/Industrial::Crusher': { instrumentVolume: 28, outputGain: 1 },
  'Subtractive::Noise/Industrial::Distorted Drone': { instrumentVolume: 28, outputGain: 1 },
  'Subtractive::Noise/Industrial::Grinder': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Noise/Industrial::Machine Rhythm': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Noise/Industrial::Metallic Clang': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Noise/Industrial::Pneumatic Hiss': { instrumentVolume: 32, outputGain: 1 },
  'Subtractive::Noise/Industrial::Siren Industrial': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Noise/Industrial::Voltage Crack': { instrumentVolume: 30, outputGain: 1 },
  'Subtractive::Noise/Industrial::White Noise Sweep': { instrumentVolume: 28, outputGain: 1 },
  'Subtractive::Organ::Church Organ': { instrumentVolume: 57, outputGain: 1 },
  'Subtractive::Organ::Combo Organ (Farfisa)': { instrumentVolume: 59, outputGain: 1 },
  'Subtractive::Organ::Drawbar Organ (B3)': { instrumentVolume: 58, outputGain: 1 },
  'Subtractive::Organ::Farfisa': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Organ::Gospel Organ': { instrumentVolume: 63, outputGain: 1 },
  'Subtractive::Organ::Jazz Organ': { instrumentVolume: 65, outputGain: 1 },
  'Subtractive::Organ::Pipe Organ': { instrumentVolume: 69, outputGain: 1 },
  'Subtractive::Organ::Rock Organ': { instrumentVolume: 59, outputGain: 1 },
  'Subtractive::Organ::Rock Organ II': { instrumentVolume: 36, outputGain: 1 },
  'Subtractive::Organ::Synth Accordion': { instrumentVolume: 78, outputGain: 1 },
  'Subtractive::Pads::Analog Choir': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Pads::Atmosphere': { instrumentVolume: 95, outputGain: 1 },
  'Subtractive::Pads::Cathedral': { instrumentVolume: 78, outputGain: 1 },
  'Subtractive::Pads::Choir Pad': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Pads::Dark Matter': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Pads::Dark Pad': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Pads::Frozen Pad': { instrumentVolume: 88, outputGain: 1 },
  'Subtractive::Pads::Glass Pad': { instrumentVolume: 81, outputGain: 1 },
  'Subtractive::Pads::Glass Pad II': { instrumentVolume: 78, outputGain: 1 },
  'Subtractive::Pads::PWM Pad': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Pads::PWM Pad II': { instrumentVolume: 99, outputGain: 1 },
  'Subtractive::Pads::Pulse Pad': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Pads::Shimmer Pad': { instrumentVolume: 94, outputGain: 1 },
  'Subtractive::Pads::Shimmer Pad II': { instrumentVolume: 90, outputGain: 1 },
  'Subtractive::Pads::Super Saw Pad': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Pads::Tape Pad': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Pads::Warm Blanket': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Pads::Warm Pad': { instrumentVolume: 89, outputGain: 1 },
  'Subtractive::Plucks::Banjo Pluck': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Dulcimer': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Electric Guitar (Clean)': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Kalimba': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Kalimba II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Marimba': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Music Box': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Nylon Pluck': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Steel Drum': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Steel Pluck': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Synth Acoustic Guitar': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Synth Harp': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Synth Harp Pluck': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Synth Pizzicato': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Synth Pluck': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Synth Pluck II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Plucks::Vibraphone': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Sci-Fi::Alien Hive': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Sci-Fi::Cryogenic': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Sci-Fi::Cyber Glitch': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Sci-Fi::Gravity Well': { instrumentVolume: 83, outputGain: 1 },
  'Subtractive::Sci-Fi::Ion Storm': { instrumentVolume: 68, outputGain: 1 },
  'Subtractive::Sci-Fi::Mothership': { instrumentVolume: 78, outputGain: 1 },
  'Subtractive::Sci-Fi::Phaser Beam': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Sci-Fi::Plasma Bolt': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Sci-Fi::Reactor Core': { instrumentVolume: 77, outputGain: 1 },
  'Subtractive::Sci-Fi::Stasis Field': { instrumentVolume: 57, outputGain: 1 },
  'Subtractive::Sci-Fi::Teleport': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Sci-Fi::Warp Drive': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Strings::Contrabass': { instrumentVolume: 63, outputGain: 1 },
  'Subtractive::Strings::Dark Strings': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Strings::Ethereal Strings': { instrumentVolume: 94, outputGain: 1 },
  'Subtractive::Strings::Pizz Strings': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Strings::Synth Analog Strings (Solina)': { instrumentVolume: 77, outputGain: 1 },
  'Subtractive::Strings::Synth Cello': { instrumentVolume: 68, outputGain: 1 },
  'Subtractive::Strings::Synth Cello II': { instrumentVolume: 71, outputGain: 1 },
  'Subtractive::Strings::Synth Pizzicato Strings': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Strings::Synth Solo Violin': { instrumentVolume: 78, outputGain: 1 },
  'Subtractive::Strings::Synth String Ensemble': { instrumentVolume: 74, outputGain: 1 },
  'Subtractive::Strings::Synth Violin Solo': { instrumentVolume: 80, outputGain: 1 },
  'Subtractive::Strings::Tremolo Strings': { instrumentVolume: 88, outputGain: 1 },
  'Subtractive::Textural::Deep Water': { instrumentVolume: 83, outputGain: 1 },
  'Subtractive::Textural::Ember Glow': { instrumentVolume: 80, outputGain: 1 },
  'Subtractive::Textural::Frost': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Textural::Liquid Metal': { instrumentVolume: 67, outputGain: 1 },
  'Subtractive::Textural::Moss': { instrumentVolume: 62, outputGain: 1 },
  'Subtractive::Textural::Paper Rustling': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Textural::Sandstorm': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Textural::Silk Thread': { instrumentVolume: 67, outputGain: 1 },
  'Subtractive::Textural::Stone Echo': { instrumentVolume: 80, outputGain: 1 },
  'Subtractive::Textural::Tinfoil': { instrumentVolume: 37, outputGain: 1 },
  'Subtractive::Textural::Velvet': { instrumentVolume: 76, outputGain: 1 },
  'Subtractive::Textural::Volcanic Glass': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Woodwinds::Recorder': { instrumentVolume: 76, outputGain: 1 },
  'Subtractive::Woodwinds::Synth Bassoon': { instrumentVolume: 64, outputGain: 1 },
  'Subtractive::Woodwinds::Synth Clarinet': { instrumentVolume: 63, outputGain: 1 },
  'Subtractive::Woodwinds::Synth Clarinet II': { instrumentVolume: 70, outputGain: 1 },
  'Subtractive::Woodwinds::Synth Flute': { instrumentVolume: 74, outputGain: 1 },
  'Subtractive::Woodwinds::Synth Oboe': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Woodwinds::Synth Oboe II': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::Woodwinds::Synth Pan Flute': { instrumentVolume: 70, outputGain: 1 },
  'Subtractive::Woodwinds::Synth Pan Flute II': { instrumentVolume: 86, outputGain: 1 },
  'Subtractive::Woodwinds::Synth Soft Flute': { instrumentVolume: 78, outputGain: 1 },
  'Subtractive::World::Erhu': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Gamelan Bell': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Gamelan Gong': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Guzheng Pluck': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Koto Pluck': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Ngoni': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Oud Pluck': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Saz': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Shamisen': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Sitar Drone': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Steel Drum': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Synth Didgeridoo': { instrumentVolume: 100, outputGain: 1 },
  'Subtractive::World::Synth Didgeridoo Drone': { instrumentVolume: 73, outputGain: 1 },
  'Subtractive::World::Synth Shakuhachi': { instrumentVolume: 76, outputGain: 1 },
  'Subtractive::World::Tanpura Drone': { instrumentVolume: 83, outputGain: 1 },
  'Subtractive::World::Zurna': { instrumentVolume: 100, outputGain: 1 },
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
  var currentExerciseEvents = [];
  var currentLightFrame = [];
  var pendingGripAttempts = null;
  var pendingGripTimer = null;
  var GRIP_COLLECTION_GRACE_MS = 80;
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
  var exquisUserKeyModeAuthorityUntil = 0;
  var exquisKeyModeSyncTimers = [];
  var lastExquisPadPalette = {};
  var lastExquisPadEffect = {};
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
  var pendingReleaseStrumCommits = [];
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
    workspace: 'practice',
    coachOpen: false,
    launchGateOpen: true,
    studioTab: 'hardware',
    soundTab: 'voice',
    hand: 'left',
    exerciseId: 'root_octave',
    exerciseFamily: 'technique',
    progressionGenre: 'starter',
    scaleId: 'ionian',
    strategyId: 'natural_clusters',
    view: 'practice',
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
    activeMidiCellIds: {},
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
    exquisCustomScaleActive: false,
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
    gripFingeringOption: 'primary',
    harmonyQuality: 'major',
    harmonyInversion: 0,
    progressionVoicing: { noteCount: 3, inversion: 0, overrides: {} },
    repertoireSectionId: '',
    repertoireTempo: 0,
    repertoireMastery: {},
    heldNotes: {},
    channelNotes: {},
    correctCount: 0,
    missCount: 0,
    streak: 0,
    calibrated: {},
    mismatched: {}
  };
  var els = {};
  var workspaceHomes = {};
  var physicalPluckedOneShotSequence = 0;

  function logEvent(kind, message) {
    var stamp = new Date().toLocaleTimeString();
    pendingLogs.push(stamp + ' [' + kind + '] ' + message);
    scheduleLogFlush();
  }

  function diagnosticNowMs() {
    return window.performance && window.performance.now ? window.performance.now() : Date.now();
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
    if (logs.length > 220) logs.shift();
    if (logs.length > 220) logs = logs.slice(logs.length - 220);
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
    state.activeMidiCellIds = {};
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

  function rememberChannelHeldNote(channel, midi) {
    if (channel === null || channel === undefined) return;
    var key = String(channel);
    if (!state.channelNotes[key]) state.channelNotes[key] = {};
    state.channelNotes[key][midi] = true;
  }

  function forgetChannelHeldNote(channel, midi) {
    if (channel === null || channel === undefined) return;
    var key = String(channel);
    var notes = state.channelNotes[key];
    if (!notes) return;
    delete notes[midi];
    if (!Object.keys(notes).length) delete state.channelNotes[key];
  }

  function channelHeldMidiNotes(channel) {
    var notes = state.channelNotes[String(channel)] || {};
    return Object.keys(notes).map(function(midi) { return parseInt(midi, 10); }).filter(function(midi) { return Number.isFinite(midi); });
  }

  function heldMidiActivitySummary() {
    var held = Object.keys(state.heldNotes).map(function(key) {
      return state.heldNotes[key];
    }).filter(Boolean).sort(function(a, b) {
      if (a.midi !== b.midi) return a.midi - b.midi;
      return (a.channel || 0) - (b.channel || 0);
    });
    if (!held.length) return 'Held: none';
    return 'Held: ' + held.map(function(note) {
      var pressure = typeof note.pressure === 'number' ? note.pressure : (note.velocity || 0);
      return noteLabelFromMidi(note.midi) + ' p' + Math.max(0, Math.min(127, Math.round(pressure || 0)));
    }).join(', ');
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
        'poolStack=' + (typeof pool.freeStack === 'number' ? pool.freeStack : 'n/a'),
        'poolPeak=' + (typeof pool.peakUsage === 'number' ? pool.peakUsage : 'n/a'),
        'steals=' + (typeof pool.steals === 'number' ? pool.steals : 'n/a'),
        'poolTotal=' + (typeof pool.totalAllocated === 'number' ? pool.totalAllocated : 'n/a')
      );
    } else {
      parts.push('poolActive=n/a', 'poolAvail=n/a', 'poolStack=n/a', 'poolPeak=n/a', 'steals=n/a', 'poolTotal=n/a');
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
      lastMidi: state.lastMidi ? {
        midi: state.lastMidi.midi,
        velocity: state.lastMidi.velocity,
        cellId: state.lastMidi.cellId,
        cellIds: (state.lastMidi.cellIds || []).slice()
      } : null,
      ssliActiveOscillators: getSsliActiveOscillatorCount(),
      lastAppliedSsliPresetKey: lastAppliedSsliPresetKey,
      soundPresetId: state.soundPresetId,
      pendingReleaseStrumCommits: pendingReleaseStrumCommits.map(function(pending) {
        var event = pending && pending.event;
        return event ? {
          note: noteLabelFromMidi(event.midi),
          midi: event.midi,
          channel: event.channel,
          ageMs: Math.round(diagnosticNowMs() - (event.releasedAtMs || diagnosticNowMs())),
          releaseIntent: event.releaseIntent || event.velocity || 0,
          peakPressure: event.releasePeakPressure || 0,
          timerActive: !!pending.timer
        } : null;
      }).filter(Boolean),
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
      }),
      exerciseEvents: currentExerciseEvents.map(function(event) {
        return {
          id: event.id,
          type: event.type,
          valid: event.valid,
          musicalIntent: event.musicalIntent,
          cellId: event.cellId,
          midi: event.midi,
          targets: event.targets.map(function(target) { return { cellId: target.cellId, midi: target.midi, pc: target.pc }; }),
          fingering: { primary: event.fingering.primary, alternatives: event.fingering.alternatives.slice() },
          timing: { mode: event.timing.mode }
        };
      })
    };
  }

  window.__exquisDebugSnapshot = getExquisDebugSnapshot;
  window.__exquisDebugBuildGripExerciseEvent = createGripExerciseEvent;
  window.__exquisDebugBuildHarmonyGripFixture = buildHarmonyGripFixture;
  window.__exquisDebugBuildProgressionFixture = buildProgressionFixture;
  window.__exquisDebugBuildSsliProgressionFixture = buildSsliProgressionFixture;
  window.__exquisDebugPromptMidis = function() { return getPromptMidis(expectedExerciseEvent()); };
  window.__exquisDebugShouldUseSsliPlayback = shouldUseSsliPlayback;
  window.__exquisDebugStartAfterAudioResume = startAfterAudioResume;
  window.__exquisDebugBuildVoiceLeadingTransition = buildVoiceLeadingTransition;
  window.__exquisDebugBuildExerciseLifecycleEvents = buildDebugExerciseLifecycleEvents;
  window.__exquisDebugEvaluateGrip = evaluateGripAttempt;
  window.__exquisLightDebug = {
    currentFrame: function() { return { pads: currentLightFrame.map(function(pad) { return Object.assign({}, pad); }) }; },
    hardwareFrame: function() { return currentLightFrame.map(function(pad) { return { padId: pad.padId, midi: pad.midi, role: pad.role, isTarget: pad.isTarget, paletteIndex: lightFramePaletteIndex(pad) }; }); },
    paletteRgbFor: function(pad) { return lightFramePaletteRgb(pad, getScale()); },
    intervalHue: intervalHue
  };

  function mod(n, m) {
    return ((n % m) + m) % m;
  }

  function noteName(midi) {
    var names = FLAT_KEY_ROOTS.indexOf(state.tonicPc) >= 0 ? NOTES_FLAT : NOTES_SHARP;
    return names[mod(midi, 12)];
  }

  function tonicNameForPc(pc) {
    pc = mod(pc, 12);
    for (var i = 0; i < TONICS.length; i++) {
      if (TONICS[i].pc === pc) return TONICS[i].name;
    }
    return NOTES_SHARP[pc];
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
  var EXQUIS_KEY_MODE_COMMAND_GAP_MS = 45;
  var EXQUIS_LED_COMMAND_GAP_MS = 12;
  var EXQUIS_PAD_COUNT = 61;

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
    if (state.exquisSyncEnabled && Date.now() < exquisUserKeyModeAuthorityUntil) {
      logEvent('midi', 'Exquis sync ignored stale root readback during local key/mode update');
      return;
    }
    cancelPendingExquisKeyModeSync();
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
    if (state.exquisSyncEnabled && Date.now() < exquisUserKeyModeAuthorityUntil) {
      logEvent('midi', 'Exquis sync ignored stale scale readback during local key/mode update');
      return;
    }
    cancelPendingExquisKeyModeSync();
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
    var sslProgression = getSsliProgressionByExerciseId(state.exerciseId);
    if (sslProgression) return sslProgression.exercise;
    var repertoireLesson = repertoireLessonForId(state.exerciseId);
    if (repertoireLesson) {
      return {
        id: repertoireLesson.id,
        name: repertoireLesson.name,
        family: 'repertoire',
        prompt: repertoireLesson.style + ' repertoire at ' + String(repertoireLesson.tempo) + ' BPM.'
      };
    }
    return EXERCISES[0];
  }

  function ssliProgressionExerciseId(genreIndex, progressionIndex) {
    return 'ssli_progression_' + genreIndex + '_' + progressionIndex;
  }

  function ssliProgressionDisplayName(progression) {
    var name = progression && progression.name ? progression.name : 'Untitled progression';
    var usage = progression && progression.usage ? progression.usage : '';
    return usage ? name + ' - ' + usage : name;
  }

  function getSsliProgressionByExerciseId(exerciseId) {
    var match = /^ssli_progression_(\d+)_(\d+)$/.exec(exerciseId || '');
    if (!match) return null;
    var genreIndex = parseInt(match[1], 10);
    var progressionIndex = parseInt(match[2], 10);
    var group = SSLI_PROGRESSION_GROUPS[genreIndex];
    var progression = group && group.progressions && group.progressions[progressionIndex];
    if (!progression) return null;
    return {
      genreIndex: genreIndex,
      progressionIndex: progressionIndex,
      group: group,
      progression: progression,
      exercise: {
        id: exerciseId,
        name: ssliProgressionDisplayName(progression),
        family: 'progressions',
        prompt: group.genre + ': ' + (progression.usage || 'SSLI progression library')
      }
    };
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
    var freshSrc = 'ssli/index.html?exhibitHost=1&v={{BUILD_TIMESTAMP_UTC}}';
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
    var presetApplied = applySelectedSsliPreset();
    if (!shouldUseSsliPlayback(presetApplied, hasSsliInstrumentOutput(SL))) {
      logEvent('audio', 'SSLI playback deferred to local fallback ' + noteLabelFromMidi(midi) + ' presetApplied=' + Boolean(presetApplied));
      return false;
    }
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

  function exerciseFamilyForId(exerciseId) {
    for (var i = 0; i < EXERCISES.length; i++) {
      if (EXERCISES[i].id === exerciseId) return EXERCISES[i].family || 'technique';
    }
    if (getSsliProgressionByExerciseId(exerciseId)) return 'progressions';
    if (repertoireLessonForId(exerciseId)) return 'repertoire';
    return 'technique';
  }

  function shouldUseSsliPlayback(presetApplied, hasOutput) {
    return Boolean(presetApplied && hasOutput);
  }

  function pressureToSsliExpression(pressure, onsetVelocity, interactionType) {
    var level = Math.max(0, Math.min(1, (pressure || 0) / 127));
    var velocityLevel = Math.max(1 / 127, Math.min(1, (onsetVelocity || pressure || 1) / 127));
    // Source for pressure/velocity ranges: MIDI Association, MIDI 1.0
    // Detailed Specification, Channel Voice Messages define note-on velocity
    // and channel/poly pressure as 7-bit performance controls. Dynamics here
    // are interaction-specific: sustained pressure-swell instruments use
    // current pressure as the loudness control, while onset-decay instruments
    // keep pressure from re-amplifying the struck/plucked excitation.
    var gain = interactionType === 'pressure-swell' ? level : (level / velocityLevel);
    return {
      cutoffHz: 900 + level * 9100,
      gain: Math.max(0, Math.min(12, gain))
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
    var presetName = state.soundPresetId && state.soundPresetId.indexOf('::') >= 0
      ? state.soundPresetId.split('::').slice(1).join('::')
      : state.soundPresetId;
    var normalizationKey = [getSsliEngineDisplayName(state.soundEngine), state.soundCategory || '', presetName || ''].join('::');
    if (SSLI_PRESET_NORMALIZATION[normalizationKey]) return SSLI_PRESET_NORMALIZATION[normalizationKey];
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
      interactionType: 'pressure-swell',
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
        interactionType: 'onset-decay',
        onsetMode: 'release-strum',
        captureWindowMs: 18,
        minInterOnsetMs: 11,
        maxSpreadMs: 46,
        order: 'physical-low-to-high',
        pressurePolicy: 'onset-only',
        // Exquis sends low-velocity brush contacts with transient pressure
        // peaks around the lower third of MIDI's 7-bit pressure range. A
        // release-strum pluck requires a deliberate contact crossing 48/127;
        // low initial velocity is still valid if pressure later rises past
        // this raw-contact threshold. Source: MIDI Association 7-bit pressure
        // range plus measured Exquis contact-noise logs.
        minReleaseIntentPressure: 48,
        immediateReleaseIntentPressure: 96,
        preContactAbsorbMs: 180,
        // Exquis release-strum is a short gesture recognizer, not a slow
        // note-off trigger. MIDI note-on/note-off are ordered 7-bit events
        // (MIDI Association, MIDI 1.0 Channel Voice messages), so the app only
        // waits long enough to catch immediate recontact/contact chatter.
        autoDampMs: SSLI_PHYSICAL_PLUCK_AUTO_DAMP_MS
      };
    }
    if (engineKey === 'physical' && physicalModel === 'strike') {
      return {
        family: 'struck',
        interactionType: 'onset-decay',
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

  function selectedInteractionType() {
    var articulation = selectedArticulation() || {};
    if (articulation.interactionType) return articulation.interactionType;
    if (articulation.family === 'plucked' || articulation.family === 'struck' || articulation.pressurePolicy === 'onset-only') return 'onset-decay';
    return 'pressure-swell';
  }

  function interactionTypeFromVoice(voice) {
    if (!voice) return selectedInteractionType();
    if (voice.interactionType) return voice.interactionType;
    if (voice.articulationFamily === 'plucked' || voice.articulationFamily === 'struck') return 'onset-decay';
    if (voice.pressurePolicy === 'onset-only' || voice.pressurePolicy === 'capture-and-apply-at-onset') return 'onset-decay';
    return selectedInteractionType();
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

  function isPendingReleaseStrumArticulation(key) {
    for (var i = 0; i < articulationQueue.length; i++) {
      var event = articulationQueue[i];
      var articulation = event && event.articulation || {};
      if (event && event.key === key && articulation.family === 'plucked' && articulation.onsetMode === 'release-strum') {
        return true;
      }
    }
    return false;
  }

  function commitReleaseStrumEvents(events, articulation) {
    if (!events.length) return;
    flushArticulationEvents(events, articulation || events[0].articulation || immediateArticulation());
  }

  function cancelPendingReleaseStrumCommitsForContact(midi) {
    var nowMs = diagnosticNowMs();
    var removed = false;
    pendingReleaseStrumCommits = pendingReleaseStrumCommits.filter(function(pending) {
      var event = pending && pending.event;
      if (!event || event.midi !== midi) return true;
      if (pending.timer) window.clearTimeout(pending.timer);
      removed = true;
      logEvent('audio', 'absorbed release-strum precontact ' + noteLabelFromMidi(event.midi) + ' on recontact age=' + Math.round(nowMs - (event.releasedAtMs || nowMs)) + 'ms releaseIntent=' + Math.round(event.releaseIntent || event.velocity || 0) + ' peakPressure=' + Math.round(event.releasePeakPressure || 0) + ' channel=' + ((event.channel || 0) + 1));
      return false;
    });
    return removed;
  }

  function releasePendingArticulation(key, releasedHeld) {
    var removed = false;
    var nowMs = Date.now();
    var releaseEvents = [];
    articulationQueue = articulationQueue.filter(function(event) {
      if (event.key !== key) return true;
      var articulation = event.articulation || {};
      var captureWindow = Math.max(0, Number(articulation.captureWindowMs || 0));
      var elapsed = nowMs - (event.enqueuedAt || nowMs);
      if (articulation.family === 'plucked' && articulation.onsetMode === 'release-strum') {
        var releaseClockMs = diagnosticNowMs();
        var heldPressure = releasedHeld && typeof releasedHeld.pressure === 'number' ? releasedHeld.pressure : 0;
        var heldPeakPressure = releasedHeld && typeof releasedHeld.peakPressure === 'number' ? releasedHeld.peakPressure : 0;
        var releaseIntent = Math.max(
          event.velocity || 0,
          heldPressure,
          heldPeakPressure
        );
        var minReleaseIntent = Math.max(1, Number(articulation.minReleaseIntentPressure || 1));
        event.releaseIntent = releaseIntent;
        event.releaseCurrentPressure = heldPressure;
        event.releasePeakPressure = heldPeakPressure;
        event.releaseHeldAgeMs = releasedHeld && releasedHeld.startedAt ? Math.max(0, Date.now() - releasedHeld.startedAt) : 0;
        logEvent('audio', 'release-strum note-up candidate ' + noteLabelFromMidi(event.midi) + ' age=' + Math.round(event.releaseHeldAgeMs || 0) + 'ms initial=' + Math.round(event.velocity || 0) + ' current=' + Math.round(heldPressure) + ' peak=' + Math.round(heldPeakPressure) + ' intent=' + Math.round(releaseIntent) + ' min=' + Math.round(minReleaseIntent) + ' channel=' + ((event.channel || 0) + 1));
        if (releaseIntent < minReleaseIntent) {
          if (event.timer) window.clearTimeout(event.timer);
          removed = true;
          logEvent('audio', 'ignored release-strum weak contact ' + noteLabelFromMidi(event.midi) + ' releaseIntent=' + Math.round(releaseIntent) + ' peakPressure=' + Math.round(heldPeakPressure) + ' min=' + Math.round(minReleaseIntent));
          return false;
        }
        event.playAfterFlushRelease = true;
        event.releasedAt = nowMs;
        event.releasedAtMs = releaseClockMs;
        event.velocity = releaseIntent;
        var immediateReleaseIntent = Math.max(minReleaseIntent, Number(articulation.immediateReleaseIntentPressure || minReleaseIntent));
        var absorbMs = Math.max(0, Number(articulation.preContactAbsorbMs || 0));
        if (absorbMs > 0 && releaseIntent < immediateReleaseIntent) {
          event.timer = window.setTimeout(function() {
            pendingReleaseStrumCommits = pendingReleaseStrumCommits.filter(function(pending) { return pending && pending.event !== event; });
            logEvent('audio', 'release-strum provisional timer fired ' + noteLabelFromMidi(event.midi) + ' age=' + Math.round(diagnosticNowMs() - (event.releasedAtMs || diagnosticNowMs())) + 'ms releaseIntent=' + Math.round(event.releaseIntent || event.velocity || 0) + ' absorb=' + Math.round(absorbMs) + 'ms channel=' + ((event.channel || 0) + 1));
            commitReleaseStrumEvents([event], event.articulation || immediateArticulation());
          }, absorbMs);
          pendingReleaseStrumCommits.push({ event: event, timer: event.timer });
          logEvent('audio', 'release-strum provisional queued ' + noteLabelFromMidi(event.midi) + ' absorb=' + Math.round(absorbMs) + 'ms releaseIntent=' + Math.round(releaseIntent) + ' immediate=' + Math.round(immediateReleaseIntent) + ' channel=' + ((event.channel || 0) + 1));
        } else {
          logEvent('audio', 'release-strum immediate commit ' + noteLabelFromMidi(event.midi) + ' releaseIntent=' + Math.round(releaseIntent) + ' immediate=' + Math.round(immediateReleaseIntent) + ' channel=' + ((event.channel || 0) + 1));
          releaseEvents.push(event);
        }
        removed = true;
        return false;
      }
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
    if (releaseEvents.length) {
      commitReleaseStrumEvents(releaseEvents, releaseEvents[0].articulation || immediateArticulation());
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
    if (canPlayReleasedCommittedPluck) {
      logEvent('audio', 'release-strum commit start ' + noteLabelFromMidi(event.midi) + ' age=' + Math.round(diagnosticNowMs() - (event.releasedAtMs || diagnosticNowMs())) + 'ms releaseIntent=' + Math.round(event.releaseIntent || event.velocity || 0) + ' heldAge=' + Math.round(event.releaseHeldAgeMs || 0) + 'ms channel=' + ((event.channel || 0) + 1));
    }
    startMidiVoice(event.key, event.midi, event.velocity, {
      expectedVoiceCount: event.expectedVoiceCount || 0,
      velocityLoadVoices: event.velocityLoadVoices || 0,
      articulationMode: event.articulation.onsetMode || '',
      articulationFamily: event.articulation.family || '',
      pressurePolicy: event.articulation.pressurePolicy || '',
      autoDampMs: event.articulation.autoDampMs || 0,
      channel: event.channel,
      interactionType: event.articulation.interactionType || '',
      releasedBeforeStart: !state.heldNotes[event.key],
      releaseIntent: event.releaseIntent || event.velocity || 0,
      releaseHeldAgeMs: event.releaseHeldAgeMs || 0,
      releasedAtMs: event.releasedAtMs || 0
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

  function flushArticulationEvents(events, articulation) {
    if (!events.length) return;
    articulation = articulation || immediateArticulation();
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
      event.playAfterFlushRelease = event.playAfterFlushRelease || (articulation.family === 'plucked' && articulation.onsetMode !== 'release-strum');
      event.timer = window.setTimeout(function() {
        startArticulatedVoice(event);
      }, delay);
    });
  }

  function flushArticulationQueue() {
    if (articulationFlushTimer) {
      window.clearTimeout(articulationFlushTimer);
      articulationFlushTimer = null;
    }
    if (!articulationQueue.length) return;
    var articulation = articulationQueue[0].articulation || immediateArticulation();
    var events = articulationQueue.slice();
    if (articulation.family === 'plucked' && articulation.onsetMode === 'release-strum') {
      events = articulationQueue.filter(function(event) { return !!event.playAfterFlushRelease; });
      articulationQueue = articulationQueue.filter(function(event) { return !event.playAfterFlushRelease; });
      if (!events.length) return;
    } else {
      articulationQueue = [];
    }
    flushArticulationEvents(events, articulation);
  }

  function scheduleMidiVoiceStart(key, midi, velocity, cellId, channel) {
    var articulation = selectedArticulation();
    var mode = articulation.onsetMode || 'immediate';
    if (mode === 'immediate' || mode === 'none') {
      startMidiVoice(key, midi, velocity, {
        channel: channel,
        articulationFamily: articulation.family || '',
        pressurePolicy: articulation.pressurePolicy || '',
        interactionType: articulation.interactionType || ''
      });
      return;
    }
    removePendingArticulation(key);
    articulationQueue.push({
      key: key,
      midi: midi,
      velocity: velocity,
      cellId: cellId || '',
      channel: channel,
      articulation: articulation,
      sequence: articulationSequence++,
      enqueuedAt: Date.now()
    });
    if (mode !== 'release-strum') {
      if (articulationFlushTimer) window.clearTimeout(articulationFlushTimer);
      articulationFlushTimer = window.setTimeout(flushArticulationQueue, Math.max(0, Number(articulation.captureWindowMs || 0)));
    }
    logEvent('audio', 'articulation queued ' + noteLabelFromMidi(midi) + ' mode=' + mode + ' family=' + (articulation.family || 'unknown') + ' capture=' + (articulation.captureWindowMs || 0) + 'ms');
  }

  function forgetHeldVoiceKey(key) {
    var voice = midiVoices[key];
    delete state.heldNotes[key];
    if (voice) {
      forgetChannelHeldNote(voice.channel, voice.midi);
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
    var interactionType = selectedInteractionType();
    var expression = pressureToSsliExpression(
      pressure,
      interactionType === 'pressure-swell' ? strongestHeldMidiVelocityForPressure(pressure) : pressure,
      interactionType
    );
    SL.audio.setExpression(expression.cutoffHz, expression.gain);
    lastSsliExpressionPressure = pressure;
    skippedSsliExpressionUpdates = 0;
    logEvent('audio', 'SSLI expression pressure=' + pressure + ' cutoff=' + Math.round(expression.cutoffHz) + 'Hz gain=' + expression.gain.toFixed(2) + ' interaction=' + interactionType);
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
    if (host && host.SynthLab) {
      var instrumentType = getCurrentSsliInstrumentType(host.SynthLab);
      if (instrumentType === 'physical') return false;
      if (instrumentType === 'fm') return false;
    }
    var strongest = strongestHeldMidiPressure();
    if (objectKeyCount(state.heldNotes) > 0 && selectedInteractionType() === 'pressure-swell') {
      setSsliMidiExpression(strongest, strongest === 0);
      return true;
    }
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

  function strongestHeldMidiVelocityForPressure(pressure) {
    var strongestVelocity = 0;
    Object.keys(state.heldNotes).forEach(function(key) {
      var held = state.heldNotes[key];
      if (!held) return;
      var heldPressure = typeof held.pressure === 'number' ? held.pressure : (held.velocity || 0);
      if (heldPressure === pressure) {
        strongestVelocity = Math.max(strongestVelocity, playableSsliMidiVelocity(held.velocity || heldPressure || 1));
      }
    });
    return strongestVelocity || pressure || 1;
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
    Object.keys(state.heldNotes).forEach(function(key) {
      var held = state.heldNotes[key];
      if (!held || held.midi !== midi || key === nextKey) return;
      if (pendingShortNoteReleases[key]) {
        window.clearTimeout(pendingShortNoteReleases[key]);
        delete pendingShortNoteReleases[key];
      }
      if (held.rawMidi !== undefined) delete pendingShortRawReleases[held.rawMidi];
      removePendingArticulation(key);
      forgetChannelHeldNote(held.channel, held.midi);
      delete state.heldNotes[key];
      logEvent('audio', 'cancelled duplicate pending MIDI note ' + noteLabelFromMidi(midi) + ' from ' + key);
    });
    Object.keys(midiVoices).forEach(function(key) {
      var voice = midiVoices[key];
      if (!voice || voice.midi !== midi || key === nextKey) return;
      if (voice.oneShot && voice.articulationFamily === 'plucked' && voice.interactionType === 'onset-decay' && !state.heldNotes[key]) {
        return;
      }
      forgetHeldVoiceKey(key);
      releaseMidiVoice(key, true);
      logEvent('audio', 'released duplicate MIDI voice ' + noteLabelFromMidi(midi) + ' from ' + key);
    });
  }

  function dampReleasedPluckedOneShotsForSamePitchContact(midi) {
    var articulation = selectedArticulation();
    if (!articulation || articulation.family !== 'plucked' || articulation.onsetMode !== 'release-strum') return;
    Object.keys(midiVoices).forEach(function(key) {
      var voice = midiVoices[key];
      if (!voice || voice.midi !== midi || !voice.oneShot || voice.articulationFamily !== 'plucked' || voice.interactionType !== 'onset-decay') return;
      if (state.heldNotes[key]) return;
      var host = getSsliHost();
      var SL = host && host.SynthLab;
      var voiceInst = SL && SL.audio && SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
      if (typeof voice.physicalInstId === 'number') voiceInst = voice.physicalInstId;
      if (SL && SL.physical && SL.physical.silenceVoice && voice.physicalVoiceId) {
        // Same pitch on a new MPE channel is still the same physical key/string.
        // This is ownership retirement for the old contact, not a second
        // acoustic event. Source: Smith, Physical Audio Signal Processing,
        // digital waveguide terminations as absorbing boundaries.
        SL.physical.silenceVoice(voice.physicalVoiceId, voiceInst);
        if (voice.oneShotCleanupTimer) window.clearTimeout(voice.oneShotCleanupTimer);
        delete midiVoices[key];
        logEvent('audio', 'silenced same-key release pluck on recontact ' + noteLabelFromMidi(voice.midi) + ' voice=' + voice.physicalVoiceId);
        logMidiVoiceStats('after-one-shot-release ' + noteLabelFromMidi(voice.midi));
      }
    });
  }

  function forgetInactiveReleasedPluckedOneShotsForNewContact() {
    var articulation = selectedArticulation();
    if (!articulation || articulation.family !== 'plucked' || articulation.onsetMode !== 'release-strum') return;
    Object.keys(midiVoices).forEach(function(key) {
      var voice = midiVoices[key];
      if (!voice || !voice.oneShot || voice.articulationFamily !== 'plucked' || voice.interactionType !== 'onset-decay') return;
      if (state.heldNotes[key]) return;
      var host = getSsliHost();
      var SL = host && host.SynthLab;
      var voiceInst = SL && SL.audio && SL.audio.getCurrentInstrument ? SL.audio.getCurrentInstrument() : 0;
      if (typeof voice.physicalInstId === 'number') voiceInst = voice.physicalInstId;
      var hasOwnedVoice = SL && SL.physical && voice.physicalVoiceId;
      var isActive = hasOwnedVoice && SL.physical.isVoiceActive ? SL.physical.isVoiceActive(voice.physicalVoiceId, voiceInst) : false;
      if (hasOwnedVoice && SL.physical.isVoiceActive && !isActive) {
        if (voice.oneShotCleanupTimer) window.clearTimeout(voice.oneShotCleanupTimer);
        delete midiVoices[key];
        logMidiVoiceStats('after-one-shot-expire ' + noteLabelFromMidi(voice.midi));
      }
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
    var interactionType = selectedInteractionType();
    if (instrumentType === 'subtractive' && interactionType === 'pressure-swell') {
      playableVelocity = 127;
    }
    var fmVelocity = playableFmMidiVelocity(velocity);
    if (physicalModel === 'strike') {
      playableVelocity = Math.max(8, Math.round(playableVelocity * 0.25));
    }
    if (instrumentType === 'physical') {
      logEvent('audio', 'SSLI physical velocity shaped raw=' + Math.max(1, velocity || 1) + ' playable=' + playableVelocity + ' heldPhysical=' + heldPhysicalVoices + ' effectiveHeld=' + effectiveHeldPhysicalVoices + ' model=' + physicalModel + (options.expectedVoiceCount ? ' expectedVoices=' + options.expectedVoiceCount : ''));
    }
    logEvent('audio', 'SSLI call startSustainedNote midi=' + midi + ' note=' + noteLabelFromMidi(midi) + ' inst=' + inst + ' engine=' + instrumentType + ' interaction=' + interactionType + ' activeBefore=' + heldSsliVoiceCount());
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
    var postStartOscs = SL.audio.getActiveOscillators ? SL.audio.getActiveOscillators() : null;
    if (postStartOscs && postStartOscs.has && !postStartOscs.has(midi)) {
      var postStartPool = SL.audio.getVoicePoolStats ? SL.audio.getVoicePoolStats() : null;
      logEvent('audio', 'SSLI MIDI sustain failed ' + noteLabelFromMidi(midi) + ' missing active oscillator after start' + (postStartPool ? ' poolActive=' + postStartPool.currentlyActive + ' poolAvail=' + postStartPool.available + ' poolStack=' + (typeof postStartPool.freeStack === 'number' ? postStartPool.freeStack : 'n/a') + ' poolTotal=' + postStartPool.totalAllocated + ' steals=' + postStartPool.steals : ''));
      return false;
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
    var durationMs = Math.max(120, Math.min(600, Number(options.oneShotMs || SSLI_PHYSICAL_PLUCK_ONE_SHOT_MS)));
    var physicalVoiceId = options.physicalVoiceId || ('exquis-pluck-' + (++physicalPluckedOneShotSequence));
    options.physicalVoiceId = physicalVoiceId;
    SL.physical.noteOn(midi, playableVelocity, inst, { maxDurationMs: durationMs, voiceId: physicalVoiceId });
    state.audioStatus = 'Audio: SSLI plucked ' + noteLabelFromMidi(midi) + '.';
    logEvent('audio', 'SSLI plucked one-shot ' + noteLabelFromMidi(midi) + ' velocity=' + playableVelocity + ' pressure=' + Math.max(1, velocity || 1) + ' voice=' + physicalVoiceId + (options.releasedBeforeStart ? ' releaseAge=' + Math.round(diagnosticNowMs() - (options.releasedAtMs || diagnosticNowMs())) + 'ms releaseIntent=' + Math.round(options.releaseIntent || velocity || 0) + ' heldAge=' + Math.round(options.releaseHeldAgeMs || 0) + 'ms' : '') + ' decay=natural preset=' + state.soundPresetId);
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
          { wave: 'triangle', oct: 0, detune: 0, level: 80 },
          { wave: 'sine', oct: 1, detune: 0, level: 22 }
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
    startAfterAudioResume(ctx, function() {
      startFallbackNote(ctx, midi, duration, localOnly);
    }).catch(function(err) {
      logEvent('audio', 'playNote aborted: audio context resume failed ' + (err && err.message ? err.message : err));
      render();
    });
  }

  function startAfterAudioResume(ctx, start) {
    if (!ctx || ctx.state === 'closed') return Promise.resolve(false);
    if (ctx.state === 'suspended' && ctx.resume) {
      var resumeResult;
      try {
        resumeResult = ctx.resume();
      } catch (err) {
        return Promise.reject(err);
      }
      return Promise.resolve(resumeResult).then(function() {
        if (ctx.state === 'closed') return false;
        start();
        return true;
      });
    }
    start();
    return Promise.resolve(true);
  }

  function startFallbackNote(ctx, midi, duration, localOnly) {
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
        channel: options.channel,
        pressurePolicy: options.pressurePolicy || 'onset-only',
        articulationFamily: options.articulationFamily || 'plucked',
        interactionType: options.interactionType || 'onset-decay',
        physicalVoiceId: options.physicalVoiceId || '',
        physicalInstId: oneShotSL && oneShotSL.audio && oneShotSL.audio.getCurrentInstrument ? oneShotSL.audio.getCurrentInstrument() : 0,
        oneShotCleanupAt: Date.now() + Math.max(120, Math.min(600, Number(options.oneShotMs || SSLI_PHYSICAL_PLUCK_ONE_SHOT_MS))) + 40
      };
      // Karplus-Strong plucks decay through loop damping after excitation.
      // Original source: Karplus & Strong (1983), CMJ 7(2). A later same-string
      // press is a physical finger mute handled by the model's noteOff.
      midiVoices[key].oneShotNoteOffSent = true;
      logEvent('audio', 'SSLI plucked one-shot natural decay ' + noteLabelFromMidi(midi));
      var scheduleOneShotCleanupCheck = function() {
        var voice = midiVoices[key];
        if (!voice || !voice.oneShot) return;
        if (state.heldNotes[key]) {
          voice.oneShotCleanupTimer = window.setTimeout(scheduleOneShotCleanupCheck, 120);
          return;
        }
        // AudioWorklet state is asynchronous: its synchronous isVoiceActive()
        // conservatively reports true. The bounded maxDurationMs passed to
        // physical.noteOn is the ownership contract, so retire bookkeeping at
        // that deadline rather than retaining a local voice forever.
        var remainingCleanupMs = Math.max(0, (voice.oneShotCleanupAt || Date.now()) - Date.now());
        if (remainingCleanupMs > 0) {
          voice.oneShotCleanupTimer = window.setTimeout(scheduleOneShotCleanupCheck, Math.min(120, remainingCleanupMs));
          return;
        }
        delete midiVoices[key];
        logMidiVoiceStats('after-one-shot-expire ' + noteLabelFromMidi(midi));
      };
      midiVoices[key].oneShotCleanupTimer = window.setTimeout(scheduleOneShotCleanupCheck, 120);
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
        channel: options.channel,
        pressurePolicy: options.pressurePolicy || '',
        articulationFamily: options.articulationFamily || '',
        interactionType: options.interactionType || selectedInteractionType()
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
      channel: options.channel,
      pressurePolicy: options.pressurePolicy || '',
      articulationFamily: options.articulationFamily || '',
      interactionType: options.interactionType || selectedInteractionType(),
      startedAt: Date.now()
    };
    state.audioStatus = 'Audio: MIDI voice ' + noteLabelFromMidi(midi) + '.';
    logEvent('audio', 'MIDI voice start ' + noteLabelFromMidi(midi) + ' velocity=' + playableVelocity + ' pressure=' + Math.max(1, velocity || 1) + ' preset=' + state.soundPresetId + ' gain=' + targetGain.toFixed(3) + ' attack=' + Math.round(attackSeconds * 1000) + 'ms ctx=' + ctx.state);
    startAudioScope();
  }

  function updateMidiVoicePressure(key, pressure) {
    var voice = midiVoices[key];
    if (!voice) return;
    if (interactionTypeFromVoice(voice) === 'onset-decay') {
      if (!voice.skippedOnsetOnlyPressure) {
        voice.skippedOnsetOnlyPressure = true;
        logEvent('audio', (voice.ssli ? 'SSLI ' : 'local ') + (voice.articulationFamily || 'onset-decay') + ' pressure ignored after onset ' + noteLabelFromMidi(voice.midi));
      }
      return;
    }
    if (voice.ssli) {
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

  function releaseMidiVoice(key, immediate, releasedHeld) {
    releasePendingArticulation(key, releasedHeld);
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
    var event = expectedExerciseEvent();
    if (!event || !event.targets.length) return;
    if (event.musicalIntent && Array.isArray(event.musicalIntent.promptMidis)) {
      var promptMidis = event.musicalIntent.promptMidis.slice();
      setFeedback('Listen for the interval, then answer with the matching shape.', 'neutral');
      playNote(promptMidis[0], 0.42);
      window.setTimeout(function() { playNote(promptMidis[1], 0.52); }, 470);
      render();
      return;
    }
    getPromptMidis(event).forEach(function(midi, index) {
      window.setTimeout(function() { playNote(midi, 0.62); }, index * 14);
    });
  }

  function playTestTone() {
    playNote(60, 0.7, true);
  }

  function resetConsole() {
    if (!window.confirm('Clear the visible diagnostics log? This cannot be undone.')) return;
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
    if (els.practiceTools) els.practiceTools.open = true;
    if (state.workspace === 'studio' && els.midiCoachSection && els.consolePanel) {
      els.midiCoachSection.appendChild(els.consolePanel);
    }
    if (els.consolePanel) {
      els.consolePanel.hidden = false;
      els.consolePanel.classList.add('expanded');
      if (els.diagnosticLog) els.diagnosticLog.scrollTop = els.diagnosticLog.scrollHeight;
    }
  }

  function playPath() {
    var ctx = ensureAudio();
    if (!ctx || !currentExerciseEvents.length) return;
    for (var i = 0; i < currentExerciseEvents.length; i++) {
      (function(idx) {
        window.setTimeout(function() {
          state.step = idx;
          render();
          var event = currentExerciseEvents[idx];
          if (event && event.targets.length) playNote(event.targets[0].midi, 0.38);
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

  function validateExerciseEvent(event) {
    var errors = [];
    var targetRequired = { note: true, grip: true, hold: true, release: true };
    if (!event || !event.id || !event.type) errors.push('missing event identity');
    if (event && !targetRequired[event.type] && event.type !== 'shift') errors.push('unsupported event type');
    if (!event || !event.musicalIntent || !event.musicalIntent.type) errors.push('missing musical intent');
    if (!event || !Array.isArray(event.targets) || (targetRequired[event.type] && !event.targets.length)) errors.push('missing targets');
    var seenTargetIds = {};
    (event && event.targets || []).forEach(function(target) {
      if (!target || !target.cellId || typeof target.midi !== 'number') errors.push('invalid target');
      else if (seenTargetIds[target.cellId]) errors.push('duplicate target');
      else seenTargetIds[target.cellId] = true;
    });
    if (!event || !event.fingering || typeof event.fingering.primary !== 'number') errors.push('missing fingering');
    if (!event || !event.timing || !event.timing.mode) errors.push('missing timing');
    if (event && event.type === 'shift' && (!event.movement || event.movement.type !== 'position-shift')) errors.push('shift requires movement');
    if (event && event.type === 'grip') {
      if (event.targets.length < 2) errors.push('grip requires multiple targets');
      if (!event.timing || event.timing.mode !== 'simultaneous') errors.push('grip must be simultaneous');
      var assignments = event.fingering && event.fingering.assignments;
      if (!Array.isArray(assignments) || assignments.length !== event.targets.length) {
        errors.push('grip requires one finger assignment per target');
      } else {
        var targetIds = {};
        var assignmentIds = {};
        event.targets.forEach(function(target) { targetIds[target.cellId] = true; });
        assignments.forEach(function(assignment) {
          if (!assignment || !targetIds[assignment.cellId] || typeof assignment.finger !== 'number' || assignmentIds[assignment.cellId]) {
            errors.push('invalid grip finger assignment');
          } else {
            assignmentIds[assignment.cellId] = true;
          }
        });
        event.targets.forEach(function(target) {
          if (!assignmentIds[target.cellId]) errors.push('grip target has no finger assignment');
        });
      }
    }
    return errors;
  }

  function finalizeExerciseEvent(event) {
    event.validationErrors = validateExerciseEvent(event);
    event.valid = event.validationErrors.length === 0;
    return event;
  }

  function copyExerciseTargets(targets) {
    return (targets || []).map(function(target) {
      return { cellId: target.cellId, midi: target.midi, pc: target.pc };
    });
  }

  function createNoteExerciseEvent(spec) {
    spec = spec || {};
    return finalizeExerciseEvent({
      id: spec.id || 'note',
      type: 'note',
      musicalIntent: spec.musicalIntent || { type: 'note' },
      cellId: spec.cellId,
      midi: spec.midi,
      sourceCell: spec.sourceCell || null,
      targets: copyExerciseTargets(spec.targets),
      fingering: spec.fingering || { primary: 0, alternatives: [] },
      timing: spec.timing || { mode: 'sequential' },
      remediation: spec.remediation || { type: 'repeat-event' }
    });
  }

  function createTimedTargetExerciseEvent(type, spec) {
    spec = spec || {};
    return finalizeExerciseEvent({
      id: spec.id || type,
      type: type,
      musicalIntent: spec.musicalIntent || { type: type },
      targets: copyExerciseTargets(spec.targets),
      fingering: spec.fingering || { primary: 0, alternatives: [] },
      timing: spec.timing || { mode: type, durationMs: spec.durationMs || 0 },
      remediation: spec.remediation || { type: 'repeat-event' }
    });
  }

  function createShiftExerciseEvent(spec) {
    spec = spec || {};
    return finalizeExerciseEvent({
      id: spec.id || 'shift',
      type: 'shift',
      musicalIntent: spec.musicalIntent || { type: 'position-shift' },
      targets: [],
      fingering: spec.fingering || { primary: 0, alternatives: [] },
      timing: spec.timing || { mode: 'before-next' },
      movement: spec.movement || { type: 'position-shift' },
      remediation: spec.remediation || { type: 'repeat-event' }
    });
  }

  function buildDebugExerciseLifecycleEvents() {
    var target = { cellId: 'r5c3', midi: 48, pc: 0 };
    return [
      createNoteExerciseEvent({ id: 'debug-note', cellId: target.cellId, midi: target.midi, targets: [target], fingering: { primary: 5, alternatives: [] } }),
      createTimedTargetExerciseEvent('hold', { id: 'debug-hold', targets: [target], fingering: { primary: 5, alternatives: [] }, durationMs: 400 }),
      createTimedTargetExerciseEvent('release', { id: 'debug-release', targets: [target], fingering: { primary: 5, alternatives: [] } }),
      createShiftExerciseEvent({ id: 'debug-shift', fingering: { primary: 3, alternatives: [] } })
    ];
  }

  function createGripExerciseEvent(spec) {
    spec = spec || {};
    var targets = copyExerciseTargets(spec.targets);
    var assignments = (spec.fingerAssignments || []).map(function(assignment) {
      return { cellId: assignment.cellId, finger: assignment.finger };
    });
    var event = {
      id: spec.id || 'grip',
      type: 'grip',
      musicalIntent: spec.musicalIntent || { type: 'chord' },
      sourceCell: spec.sourceCell || null,
      sourceCells: spec.sourceCells || [],
      targets: targets,
      fingering: {
        primary: assignments.length ? assignments[0].finger : 0,
        alternatives: spec.fingeringAlternatives || [],
        assignments: assignments
      },
      timing: { mode: 'simultaneous', toleranceMs: 80 },
      remediation: { type: 'repeat-event' }
    };
    return finalizeExerciseEvent(event);
  }

  var HARMONY_TRIAD_INTERVALS = {
    major: [0, 4, 7],
    minor: [0, 3, 7],
    diminished: [0, 3, 6],
    augmented: [0, 4, 8]
  };

  function chordVoicingOffsets(quality, noteCount, inversion) {
    var intervals = HARMONY_TRIAD_INTERVALS[quality];
    var count = Math.max(2, Math.min(5, parseInt(noteCount, 10) || 3));
    var offsets = intervals ? intervals.slice() : [];
    if (!offsets.length) return null;
    while (offsets.length < count) offsets.push(intervals[(offsets.length - intervals.length) % intervals.length] + 12);
    offsets = offsets.slice(0, count);
    var turns = Math.max(0, Math.min(count - 1, parseInt(inversion, 10) || 0));
    for (var i = 0; i < turns; i++) offsets.push(offsets.shift() + 12);
    offsets.sort(function(a, b) { return a - b; });
    // A physical pad cannot represent the same doubled MIDI pitch twice.
    // Continue the chord-tone cycle upward when inversion creates a collision.
    for (var oi = 1; oi < offsets.length; oi++) {
      if (offsets[oi] <= offsets[oi - 1]) {
        var nextOffset = intervals[(oi + turns) % intervals.length];
        while (nextOffset <= offsets[oi - 1]) nextOffset += 12;
        offsets[oi] = nextOffset;
      }
    }
    return offsets;
  }

  function progressionVoicingForStep(step) {
    var override = state.progressionVoicing.overrides[step] || {};
    var count = override.noteCount || state.progressionVoicing.noteCount;
    var inversion = override.inversion;
    if (typeof inversion !== 'number') inversion = state.progressionVoicing.inversion;
    return { noteCount: count, inversion: Math.min(count - 1, inversion) };
  }
  var PROGRESSION_FIXTURES = {
    'c-major-i-iv-v-i': {
      label: 'I-IV-V-I',
      tonicPc: 0,
      tempo: 72,
      rhythm: 'whole-note',
      prerequisites: ['major-triad'],
      chords: [
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 },
        { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 },
        { degree: 'V', quality: 'major', rootMidi: 43, inversion: 0 },
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 }
      ]
    },
    'c-major-ii-v-i': {
      label: 'ii-V-I',
      tonicPc: 0,
      tempo: 72,
      rhythm: 'whole-note',
      prerequisites: ['major-triad', 'minor-triad'],
      chords: [
        { degree: 'ii', quality: 'minor', rootMidi: 50, inversion: 0 },
        { degree: 'V', quality: 'major', rootMidi: 43, inversion: 0 },
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 }
      ]
    },
    'c-major-i-v-vi-iv': {
      label: 'I-V-vi-IV',
      tonicPc: 0,
      tempo: 84,
      rhythm: 'whole-note',
      prerequisites: ['major-triad', 'minor-triad'],
      chords: [
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 },
        { degree: 'V', quality: 'major', rootMidi: 43, inversion: 0 },
        { degree: 'vi', quality: 'minor', rootMidi: 45, inversion: 0 },
        { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 }
      ]
    },
    'c-major-i-vi-ii-v': {
      label: 'I-vi-ii-V',
      tonicPc: 0,
      tempo: 80,
      rhythm: 'whole-note',
      prerequisites: ['major-triad', 'minor-triad'],
      chords: [
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 },
        { degree: 'vi', quality: 'minor', rootMidi: 45, inversion: 0 },
        { degree: 'ii', quality: 'minor', rootMidi: 50, inversion: 0 },
        { degree: 'V', quality: 'major', rootMidi: 43, inversion: 0 }
      ]
    },
    'c-major-12-bar-blues': {
      label: '12-bar blues',
      tonicPc: 0,
      tempo: 76,
      rhythm: 'one-bar',
      prerequisites: ['major-triad', 'steady-pulse'],
      chords: [
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 },
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 },
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 },
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 },
        { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 },
        { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 },
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 },
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 },
        { degree: 'V', quality: 'major', rootMidi: 43, inversion: 0 },
        { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 },
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 },
        { degree: 'V', quality: 'major', rootMidi: 43, inversion: 0 }
      ]
    },
    'c-dorian-i-iv-vamp': {
      label: 'i-IV vamp',
      modeName: 'Dorian',
      tonicPc: 0,
      tempo: 84,
      rhythm: 'whole-note',
      prerequisites: ['minor-triad', 'major-triad'],
      chords: [
        { degree: 'i', quality: 'minor', rootMidi: 36, inversion: 0 },
        { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 },
        { degree: 'i', quality: 'minor', rootMidi: 36, inversion: 0 },
        { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 }
      ]
    },
    'c-major-i-iv-vi-v': {
      label: 'I-IV-vi-V', tonicPc: 0, tempo: 84, rhythm: 'whole-note', prerequisites: ['major-triad', 'minor-triad'],
      chords: [
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 }, { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 },
        { degree: 'vi', quality: 'minor', rootMidi: 45, inversion: 0 }, { degree: 'V', quality: 'major', rootMidi: 43, inversion: 0 }
      ]
    },
    'c-major-i-iii-iv-v': {
      label: 'I-iii-IV-V', tonicPc: 0, tempo: 80, rhythm: 'whole-note', prerequisites: ['major-triad', 'minor-triad'],
      chords: [
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 }, { degree: 'iii', quality: 'minor', rootMidi: 40, inversion: 0 },
        { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 }, { degree: 'V', quality: 'major', rootMidi: 43, inversion: 0 }
      ]
    },
    'c-major-i-ii-vi-iv': {
      label: 'I-ii-vi-IV', tonicPc: 0, tempo: 84, rhythm: 'whole-note', prerequisites: ['major-triad', 'minor-triad'],
      chords: [
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 }, { degree: 'ii', quality: 'minor', rootMidi: 50, inversion: 0 },
        { degree: 'vi', quality: 'minor', rootMidi: 45, inversion: 0 }, { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 }
      ]
    },
    'c-major-circle-of-fifths': {
      label: 'circle of fifths', tonicPc: 0, tempo: 72, rhythm: 'whole-note', prerequisites: ['major-triad', 'minor-triad', 'diminished-triad'],
      chords: [
        { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 }, { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 },
        { degree: 'vii', quality: 'diminished', rootMidi: 47, inversion: 0 }, { degree: 'iii', quality: 'minor', rootMidi: 40, inversion: 0 },
        { degree: 'vi', quality: 'minor', rootMidi: 45, inversion: 0 }, { degree: 'ii', quality: 'minor', rootMidi: 50, inversion: 0 },
        { degree: 'V', quality: 'major', rootMidi: 43, inversion: 0 }, { degree: 'I', quality: 'major', rootMidi: 48, inversion: 0 }
      ]
    },
    'c-minor-i-iv-v-i': {
      label: 'i-iv-V-i', modeName: 'minor', tonicPc: 0, tempo: 72, rhythm: 'whole-note', prerequisites: ['major-triad', 'minor-triad'],
      chords: [
        { degree: 'i', quality: 'minor', rootMidi: 48, inversion: 0 }, { degree: 'iv', quality: 'minor', rootMidi: 41, inversion: 0 },
        { degree: 'V', quality: 'major', rootMidi: 43, inversion: 0 }, { degree: 'i', quality: 'minor', rootMidi: 48, inversion: 0 }
      ]
    },
    'c-minor-i-bVII-bVI-bVII': {
      label: 'i-bVII-bVI-bVII', modeName: 'minor', tonicPc: 0, tempo: 80, rhythm: 'whole-note', prerequisites: ['major-triad', 'minor-triad'],
      chords: [
        { degree: 'i', quality: 'minor', rootMidi: 48, inversion: 0 }, { degree: 'bVII', quality: 'major', rootMidi: 46, inversion: 0 },
        { degree: 'bVI', quality: 'major', rootMidi: 44, inversion: 0 }, { degree: 'bVII', quality: 'major', rootMidi: 46, inversion: 0 }
      ]
    },
    'c-dorian-i-bVII-iv': {
      label: 'i-bVII-IV', modeName: 'Dorian', tonicPc: 0, tempo: 84, rhythm: 'whole-note', prerequisites: ['major-triad', 'minor-triad'],
      chords: [
        { degree: 'i', quality: 'minor', rootMidi: 48, inversion: 0 }, { degree: 'bVII', quality: 'major', rootMidi: 46, inversion: 0 },
        { degree: 'IV', quality: 'major', rootMidi: 41, inversion: 0 }
      ]
    },
    'c-phrygian-i-bII-vamp': {
      label: 'i-bII vamp', modeName: 'Phrygian', tonicPc: 0, tempo: 76, rhythm: 'whole-note', prerequisites: ['major-triad', 'minor-triad'],
      chords: [
        { degree: 'i', quality: 'minor', rootMidi: 48, inversion: 0 }, { degree: 'bII', quality: 'major', rootMidi: 49, inversion: 0 },
        { degree: 'i', quality: 'minor', rootMidi: 48, inversion: 0 }, { degree: 'bII', quality: 'major', rootMidi: 49, inversion: 0 }
      ]
    }
  };
  var PROGRESSION_EXERCISE_FIXTURE_IDS = {
    c_major_progression: 'c-major-i-iv-v-i',
    c_major_ii_v_i: 'c-major-ii-v-i',
    major_i_v_vi_iv: 'c-major-i-v-vi-iv',
    major_i_vi_ii_v: 'c-major-i-vi-ii-v',
    major_12_bar_blues: 'c-major-12-bar-blues',
    dorian_i_iv_vamp: 'c-dorian-i-iv-vamp',
    major_i_iv_vi_v: 'c-major-i-iv-vi-v',
    major_i_iii_iv_v: 'c-major-i-iii-iv-v',
    major_i_ii_vi_iv: 'c-major-i-ii-vi-iv',
    major_circle_of_fifths: 'c-major-circle-of-fifths',
    minor_i_iv_v_i: 'c-minor-i-iv-v-i',
    minor_i_bVII_bVI_bVII: 'c-minor-i-bVII-bVI-bVII',
    dorian_i_bVII_iv: 'c-dorian-i-bVII-iv',
    phrygian_i_bII_vamp: 'c-phrygian-i-bII-vamp'
  };

  function canonicalScaleForProgressionExercise(exerciseId) {
    var fixtureId = PROGRESSION_EXERCISE_FIXTURE_IDS[exerciseId] || '';
    if (fixtureId.indexOf('c-major-') === 0) return 'ionian';
    if (fixtureId.indexOf('c-minor-') === 0) return 'aeolian';
    if (fixtureId.indexOf('c-dorian-') === 0) return 'dorian';
    if (fixtureId.indexOf('c-phrygian-') === 0) return 'phrygian';
    return '';
  }

  function applyCanonicalProgressionScale() {
    var scaleId = canonicalScaleForProgressionExercise(state.exerciseId);
    if (!scaleId) return false;
    var changed = false;
    if (state.scaleId !== scaleId) {
      state.scaleId = scaleId;
      state.rootCellId = '';
      changed = true;
    }
    if (state.view !== 'practice') {
      state.view = 'practice';
      changed = true;
    }
    return changed;
  }

  var REPERTOIRE_LESSONS = [
    {
      id: 'repertoire_anthem_progression',
      name: 'Anthem progression',
      style: 'Pop & Rock',
      tempo: 96,
      sections: [
        { id: 'verse', name: 'Verse', progressionId: 'major_i_v_vi_iv' },
        { id: 'chorus', name: 'Chorus', progressionId: 'major_i_iv_vi_v' }
      ]
    },
    {
      id: 'repertoire_12_bar_blues',
      name: '12-bar blues form',
      style: 'Blues',
      tempo: 76,
      sections: [
        { id: 'chorus', name: 'Chorus', progressionId: 'major_12_bar_blues' }
      ]
    }
  ];

  function repertoireLessonForId(id) {
    for (var i = 0; i < REPERTOIRE_LESSONS.length; i++) {
      if (REPERTOIRE_LESSONS[i].id === id) return REPERTOIRE_LESSONS[i];
    }
    return null;
  }

  function selectedRepertoireSection() {
    var lesson = repertoireLessonForId(state.exerciseId);
    if (!lesson) return null;
    var section = lesson.sections.filter(function(candidate) {
      return candidate.id === state.repertoireSectionId;
    })[0] || lesson.sections[0];
    if (section) state.repertoireSectionId = section.id;
    return section ? { lesson: lesson, section: section } : null;
  }

  function repertoireTempo(selection) {
    return Math.max(40, Math.min(240, state.repertoireTempo || selection.lesson.tempo));
  }

  function recordRepertoireLoop(event) {
    if (!event || !event.musicalIntent || !event.musicalIntent.repertoireId) return;
    if (mod(state.step, currentExerciseEvents.length) !== currentExerciseEvents.length - 1) return;
    var key = event.musicalIntent.repertoireId + ':' + event.musicalIntent.repertoireSection;
    state.repertoireMastery[key] = (state.repertoireMastery[key] || 0) + 1;
  }

  function repertoireCompletedLoopCount(selection) {
    if (!selection) return 0;
    return state.repertoireMastery[selection.lesson.id + ':' + selection.section.id] || 0;
  }

  function playRepertoireCountIn() {
    var selection = selectedRepertoireSection();
    if (!selection) return;
    var beatMs = Math.round(60000 / repertoireTempo(selection));
    setFeedback('Count in: 1, 2, 3, 4.', 'neutral');
    for (var beat = 0; beat < 4; beat++) {
      (function(index) {
        window.setTimeout(function() { playNote(index === 0 ? 84 : 72, 0.06, true); }, index * beatMs);
      })(beat);
    }
    render();
  }

  function exactMidiCandidates(cells, midi) {
    return cells.filter(function(cell) { return cell.midi === midi; });
  }

  function innerRowPenalty(cell) {
    // Rows 3 through 7 are the practical center of the Exquis surface.
    // Outer rows remain available only when a pitch has no inner placement.
    return Math.max(0, Math.abs(cell.row - 5) - 2);
  }

  function ergonomicGripScore(gripCells) {
    var minX = Infinity;
    var maxX = -Infinity;
    var minY = Infinity;
    var maxY = -Infinity;
    var centerCost = 0;
    gripCells.forEach(function(cell) {
      minX = Math.min(minX, cell.x);
      maxX = Math.max(maxX, cell.x);
      minY = Math.min(minY, cell.y);
      maxY = Math.max(maxY, cell.y);
      centerCost += centerScore(cell);
      centerCost += innerRowPenalty(cell) * 16;
    });
    // Keep simultaneous grips compact in the physical vertical direction;
    // edge-spanning voicings are harder to land together than close clusters.
    return (maxX - minX) + (maxY - minY) * 2 + centerCost * 80;
  }

  function selectErgonomicGripCells(cells, targetMidis) {
    var candidateGroups = targetMidis.map(function(midi) { return exactMidiCandidates(cells, midi); });
    if (candidateGroups.some(function(group) { return !group.length; })) return null;
    var best = null;
    var bestScore = Infinity;
    function visit(index, selected) {
      if (index === candidateGroups.length) {
        var score = ergonomicGripScore(selected);
        if (score < bestScore) {
          bestScore = score;
          best = selected.slice();
        }
        return;
      }
      candidateGroups[index].forEach(function(candidate) {
        selected.push(candidate);
        visit(index + 1, selected);
        selected.pop();
      });
    }
    visit(0, []);
    return best;
  }

  function resolvePlayableTriadRootMidi(desiredRootMidi, quality) {
    return resolvePlayableChordRootMidi(desiredRootMidi, quality, 3, 0);
  }

  function exquisChordFingerPattern(noteCount) {
    var count = Math.max(2, Math.min(5, parseInt(noteCount, 10) || 3));
    // Compact Exquis grips use consecutive physical fingers. Center short
    // spans in the hand; chord voice order, not piano keyboard direction,
    // determines which target receives each successive position.
    var firstFinger = Math.max(1, Math.ceil((6 - count) / 2));
    var fingers = [];
    for (var finger = firstFinger; finger < firstFinger + count; finger++) {
      fingers.push(finger);
    }
    return fingers;
  }

  function resolvePlayableChordRootMidi(desiredRootMidi, quality, noteCount, inversion) {
    var offsets = chordVoicingOffsets(quality, noteCount, inversion);
    var cells = makeGrid();
    if (!offsets) return null;
    var seenMidis = {};
    var best = null;
    var bestScore = Infinity;
    cells.forEach(function(cell) {
      if (cell.pc !== mod(desiredRootMidi, 12) || seenMidis[cell.midi]) return;
      seenMidis[cell.midi] = true;
      var targetMidis = offsets.map(function(offset) { return cell.midi + offset; });
      var gripCells = selectErgonomicGripCells(cells, targetMidis);
      if (!gripCells) return;
      var score = Math.abs(cell.midi - desiredRootMidi) * 32 + ergonomicGripScore(gripCells);
      if (score < bestScore) {
        bestScore = score;
        best = cell.midi;
      }
    });
    return best;
  }

  function buildHarmonyGripFixture(spec) {
    spec = spec || {};
    var noteCount = Math.max(2, Math.min(5, parseInt(spec.noteCount, 10) || 3));
    var inversion = Math.max(0, Math.min(noteCount - 1, parseInt(spec.inversion, 10) || 0));
    var offsets = chordVoicingOffsets(spec.quality, noteCount, inversion);
    if (!offsets || typeof spec.rootMidi !== 'number') return null;
    var cells = makeGrid();
    var root;
    var gripCells;
    if (spec.compactVoicing) {
      gripCells = selectErgonomicGripCells(cells, offsets.map(function(offset) { return spec.rootMidi + offset; }));
      if (!gripCells) return null;
      root = gripCells[0];
    } else {
      root = bestCellForTarget(cells, mod(spec.rootMidi, 12), spec.rootMidi, null, null);
      if (!root || root.midi !== spec.rootMidi) return null;
      gripCells = offsets.map(function(offset) {
        var targetMidi = spec.rootMidi + offset;
        var cell = bestCellForTarget(cells, mod(targetMidi, 12), targetMidi, root, null);
        return cell && cell.midi === targetMidi ? cell : null;
      });
      if (gripCells.some(function(cell) { return !cell; })) return null;
    }
    var inversionName = inversion === 0 ? 'root' : String(inversion) + (inversion === 1 ? 'st' : inversion === 2 ? 'nd' : inversion === 3 ? 'rd' : 'th');
    // Chord positions follow neighboring Exquis buttons, not piano interval spacing.
    var fingers = exquisChordFingerPattern(noteCount);
    return createGripExerciseEvent({
      id: spec.id || spec.quality + ':' + inversionName,
      musicalIntent: { type: 'triad', quality: spec.quality, inversion: inversionName },
      targets: gripCells.map(function(cell) { return { cellId: cellKey(cell), midi: cell.midi, pc: cell.pc }; }),
      fingerAssignments: gripCells.map(function(cell, index) { return { cellId: cellKey(cell), finger: fingers[index] }; }),
      sourceCell: clonePathCell(root),
      sourceCells: gripCells.map(clonePathCell)
    });
  }

  function buildProgressionFixture(id) {
    var fixture = PROGRESSION_FIXTURES[id];
    if (!fixture) return null;
    var requestedTonicPc = arguments.length > 1 && typeof arguments[1] === 'number' ? arguments[1] : state.tonicPc;
    var tonicPc = mod(requestedTonicPc, 12);
    var transposition = mod(tonicPc - (fixture.tonicPc || 0), 12);
    var events = fixture.chords.map(function(chord, index) {
      var voicing = progressionVoicingForStep(index);
      var playableRootMidi = resolvePlayableChordRootMidi(chord.rootMidi + transposition, chord.quality, voicing.noteCount, voicing.inversion);
      var event = buildHarmonyGripFixture({
        id: id + ':' + index + ':' + chord.degree,
        quality: chord.quality,
        rootMidi: playableRootMidi,
        inversion: voicing.inversion,
        noteCount: voicing.noteCount,
        compactVoicing: true
      });
      if (event) {
        event.musicalIntent.progressionId = id;
        event.musicalIntent.degree = chord.degree;
        event.musicalIntent.step = index + 1;
      }
      return event;
    });
    if (events.some(function(event) { return !event || !event.valid; })) return null;
    return {
      id: id,
      title: tonicNameForPc(tonicPc) + ' ' + (fixture.modeName || 'major') + ' ' + fixture.label,
      tonicPc: tonicPc,
      tempo: fixture.tempo,
      rhythm: fixture.rhythm,
      prerequisites: fixture.prerequisites ? fixture.prerequisites.slice() : [],
      events: events
    };
  }

  function buildSsliProgressionFixture(genreIndex, progressionIndex, tonicPc, scaleId) {
    var group = SSLI_PROGRESSION_GROUPS[genreIndex];
    var progression = group && group.progressions && group.progressions[progressionIndex];
    var mode = SSLI_MODES[scaleId || state.scaleId] || SSLI_MODES.ionian;
    var qualityMap = { maj: 'major', min: 'minor', dim: 'diminished', aug: 'augmented' };
    if (!progression || !mode || !Array.isArray(progression.degs) || !Array.isArray(mode.scale) || !Array.isArray(mode.triads)) return null;
    var resolvedTonicPc = mod(typeof tonicPc === 'number' ? tonicPc : state.tonicPc, 12);
    var roman = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii'];
    var events = progression.degs.map(function(degree, index) {
      var interval = mode.scale[degree];
      var quality = qualityMap[mode.triads[degree]];
      if (typeof interval !== 'number' || !quality) return null;
      var rootMidi = 48 + interval;
      if (rootMidi > 52) rootMidi -= 12;
      var voicing = progressionVoicingForStep(index);
      var playableRootMidi = resolvePlayableChordRootMidi(rootMidi + resolvedTonicPc, quality, voicing.noteCount, voicing.inversion);
      if (playableRootMidi === null) return null;
      var event = buildHarmonyGripFixture({
        id: ssliProgressionExerciseId(genreIndex, progressionIndex) + ':' + index,
        quality: quality,
        rootMidi: playableRootMidi,
        inversion: voicing.inversion,
        noteCount: voicing.noteCount,
        compactVoicing: true
      });
      if (event) {
        event.musicalIntent.progressionId = ssliProgressionExerciseId(genreIndex, progressionIndex);
        event.musicalIntent.degree = roman[degree] || String(degree + 1);
        event.musicalIntent.step = index + 1;
        event.musicalIntent.genre = group.genre;
        event.musicalIntent.usage = progression.usage || '';
      }
      return event;
    });
    if (events.some(function(event) { return !event || !event.valid; })) return null;
    return {
      id: ssliProgressionExerciseId(genreIndex, progressionIndex),
      title: tonicNameForPc(resolvedTonicPc) + ' ' + mode.name + ' · ' + group.genre + ' · ' + progression.name,
      genre: group.genre,
      usage: progression.usage || '',
      tempo: 80,
      rhythm: 'whole-note',
      prerequisites: ['major-triad', 'minor-triad'],
      events: events
    };
  }

  function fixtureTargetMidis(fixture) {
    return (fixture && fixture.targets || []).map(function(target) { return target.midi; }).sort(function(a, b) { return a - b; });
  }

  function buildVoiceLeadingTransition(spec) {
    spec = spec || {};
    var fromSpec = spec.from || {};
    var toSpec = spec.to || {};
    var source = buildHarmonyGripFixture({
      id: 'voice-leading-source',
      quality: fromSpec.quality,
      rootMidi: fromSpec.rootMidi,
      inversion: fromSpec.inversion
    });
    if (!source || !source.valid || !HARMONY_TRIAD_INTERVALS[toSpec.quality] || typeof toSpec.rootMidi !== 'number') return null;
    var sourceMidis = fixtureTargetMidis(source);
    var best = null;
    for (var inversion = 0; inversion < 3; inversion++) {
      var destination = buildHarmonyGripFixture({
        id: 'voice-leading-destination:' + inversion,
        quality: toSpec.quality,
        rootMidi: toSpec.rootMidi,
        inversion: inversion
      });
      if (!destination || !destination.valid) continue;
      var destinationMidis = fixtureTargetMidis(destination);
      var anchorMidis = sourceMidis.filter(function(midi) { return destinationMidis.indexOf(midi) !== -1; });
      var movementSemitones = sourceMidis.reduce(function(total, midi, index) {
        return total + Math.abs(destinationMidis[index] - midi);
      }, 0);
      var candidate = {
        from: source,
        to: destination,
        anchorMidis: anchorMidis,
        movementSemitones: movementSemitones,
        inversion: inversion
      };
      if (!best ||
          candidate.anchorMidis.length > best.anchorMidis.length ||
          (candidate.anchorMidis.length === best.anchorMidis.length && candidate.movementSemitones < best.movementSemitones) ||
          (candidate.anchorMidis.length === best.anchorMidis.length && candidate.movementSemitones === best.movementSemitones && candidate.inversion < best.inversion)) {
        best = candidate;
      }
    }
    if (!best) return null;
    delete best.inversion;
    return best;
  }

  function evaluateGripAttempt(event, attempts) {
    var targets = (event && event.targets || []).slice();
    var matched = [];
    var wrong = [];
    var usedTargets = {};
    (attempts || []).forEach(function(attempt) {
      var targetIndex = -1;
      for (var i = 0; i < targets.length; i++) {
        var target = targets[i];
        if (usedTargets[i]) continue;
        if (target.midi === attempt.midi && (!attempt.cellId || target.cellId === attempt.cellId)) {
          targetIndex = i;
          break;
        }
      }
      if (targetIndex === -1) wrong.push(attempt);
      else {
        usedTargets[targetIndex] = true;
        matched.push(attempt);
      }
    });
    var missing = targets.filter(function(_target, index) { return !usedTargets[index]; });
    var toleranceMs = event && event.timing && typeof event.timing.toleranceMs === 'number' ? event.timing.toleranceMs : 80;
    var timingSpreadMs = 0;
    if (matched.length > 1) {
      var times = matched.map(function(attempt) { return attempt.at; });
      timingSpreadMs = Math.max.apply(Math, times) - Math.min.apply(Math, times);
    }
    var complete = !wrong.length && !missing.length;
    var late = complete && timingSpreadMs > toleranceMs;
    return {
      accepted: complete && !late,
      outcome: wrong.length ? 'wrong' : (missing.length ? 'partial' : (late ? 'late' : 'complete')),
      missing: missing,
      wrong: wrong,
      timingSpreadMs: timingSpreadMs,
      toleranceMs: toleranceMs
    };
  }

  function buildPracticeExerciseEvents(path, fingers) {
    var repertoireSelection = selectedRepertoireSection();
    if (repertoireSelection) {
      var repertoireFixture = buildProgressionFixture(PROGRESSION_EXERCISE_FIXTURE_IDS[repertoireSelection.section.progressionId] || repertoireSelection.section.progressionId);
      if (!repertoireFixture) return [];
      repertoireFixture.events.forEach(function(event) {
        event.musicalIntent.repertoireId = repertoireSelection.lesson.id;
        event.musicalIntent.repertoireSection = repertoireSelection.section.id;
        event.musicalIntent.repertoireSectionName = repertoireSelection.section.name;
        event.musicalIntent.tempo = repertoireTempo(repertoireSelection);
      });
      return repertoireFixture.events;
    }
    var ssliProgression = getSsliProgressionByExerciseId(state.exerciseId);
    if (ssliProgression) {
      var generatedProgression = buildSsliProgressionFixture(ssliProgression.genreIndex, ssliProgression.progressionIndex);
      return generatedProgression ? generatedProgression.events : [];
    }
    var progressionFixtureId = PROGRESSION_EXERCISE_FIXTURE_IDS[state.exerciseId];
    if (progressionFixtureId) {
      var progression = buildProgressionFixture(progressionFixtureId);
      return progression ? progression.events : [];
    }
    var heardInterval = HEARD_INTERVAL_FIXTURES[state.exerciseId];
    if (heardInterval && path.length) {
      var heardRoot = path[0];
      var heardTarget = bestCellForTarget(makeGrid(), mod(heardRoot.midi + heardInterval.semitones, 12), heardRoot.midi + heardInterval.semitones, heardRoot, null);
      var heardCells = heardTarget && heardTarget.midi === heardRoot.midi + heardInterval.semitones ? [heardRoot, heardTarget] : [];
      if (!heardCells.length) return [];
      return [createGripExerciseEvent({
        id: state.exerciseId,
        musicalIntent: { type: 'heard-interval', quality: heardInterval.quality, promptMidis: heardCells.map(function(cell) { return cell.midi; }), concealTargets: true },
        targets: heardCells.map(function(cell) { return { cellId: cellKey(cell), midi: cell.midi, pc: cell.pc }; }),
        fingerAssignments: heardCells.map(function(cell, index) { return { cellId: cellKey(cell), finger: exquisChordFingerPattern(heardCells.length)[index] }; }),
        sourceCell: clonePathCell(heardCells[0]),
        sourceCells: heardCells.map(clonePathCell)
      })];
    }
    if (state.exerciseId === 'voice_leading' && path.length) {
      var transition = buildVoiceLeadingTransition({
        from: {
          quality: state.harmonyQuality,
          rootMidi: path[0].midi,
          inversion: state.harmonyInversion
        },
        to: {
          quality: state.harmonyQuality,
          rootMidi: path[0].midi - 7
        }
      });
      if (!transition) return [];
      transition.from.id = 'voice-leading:source';
      transition.to.id = 'voice-leading:destination';
      transition.from.musicalIntent.role = 'source';
      transition.to.musicalIntent.role = 'destination';
      transition.to.musicalIntent.anchorMidis = transition.anchorMidis.slice();
      transition.to.musicalIntent.movementSemitones = transition.movementSemitones;
      return [transition.from, transition.to];
    }
    if (state.exerciseId === 'harmony_triad' && path.length) {
      var harmonyFixture = buildHarmonyGripFixture({
        id: 'harmony-triad:' + state.harmonyQuality + ':' + state.harmonyInversion,
        quality: state.harmonyQuality,
        inversion: state.harmonyInversion,
        rootMidi: path[0].midi
      });
      return harmonyFixture ? [harmonyFixture] : [];
    }
    if ((state.exerciseId === 'major_third' || state.exerciseId === 'major_triad') && path.length >= 5) {
      var gripCells = state.exerciseId === 'major_third' ? [path[0], path[2]] : [path[0], path[2], path[4]];
      return [createGripExerciseEvent({
        id: state.exerciseId + ':root-position',
        musicalIntent: state.exerciseId === 'major_third' ? { type: 'interval', quality: 'major-third' } : { type: 'triad', quality: 'major', inversion: 'root' },
        targets: gripCells.map(function(cell) { return { cellId: cellKey(cell), midi: cell.midi, pc: cell.pc }; }),
        fingerAssignments: gripCells.map(function(cell, index) { return { cellId: cellKey(cell), finger: exquisChordFingerPattern(gripCells.length)[index] }; }),
        sourceCell: clonePathCell(gripCells[0]),
        sourceCells: gripCells.map(clonePathCell)
      })];
    }
    return path.map(function(cell, index) {
      var targetCellId = cellKey(cell);
      return createNoteExerciseEvent({
        id: state.exerciseId + ':note:' + index + ':' + targetCellId,
        musicalIntent: { type: 'scale-degree', degree: getScaleDegree(cell, getScale()) },
        cellId: targetCellId,
        midi: cell.midi,
        sourceCell: clonePathCell(cell),
        targets: [{ cellId: targetCellId, midi: cell.midi, pc: cell.pc }],
        fingering: { primary: fingers[index % fingers.length], alternatives: [] },
        timing: { mode: 'sequential' },
        remediation: { type: 'repeat-event' }
      });
    });
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

  var SCALE_HUE_ROOT = 120;
  var EXQUIS_PALETTE_OFF = 1;
  var EXQUIS_PALETTE_HUE_START = 16;
  var EXQUIS_PALETTE_ROOT = 28;

  function intervalHue(interval, scale) {
    var normalized = mod(interval, 12);
    var intervals = scale && scale.intervals ? scale.intervals : getScale().intervals;
    var degreeIndex = intervals.indexOf(normalized);
    if (degreeIndex >= 0) {
      return mod(SCALE_HUE_ROOT + Math.round(degreeIndex * 360 / intervals.length), 360);
    }
    return mod(SCALE_HUE_ROOT + Math.round(normalized * 360 / 12), 360);
  }

  function hueToExquisRgb(hue, brightness) {
    var saturation = 0.85;
    var chroma = brightness * saturation;
    var hueSector = mod(hue, 360) / 60;
    var secondary = chroma * (1 - Math.abs(mod(hueSector, 2) - 1));
    var red = 0;
    var green = 0;
    var blue = 0;
    if (hueSector < 1) {
      red = chroma;
      green = secondary;
    } else if (hueSector < 2) {
      red = secondary;
      green = chroma;
    } else if (hueSector < 3) {
      green = chroma;
      blue = secondary;
    } else if (hueSector < 4) {
      green = secondary;
      blue = chroma;
    } else if (hueSector < 5) {
      red = secondary;
      blue = chroma;
    } else {
      red = chroma;
      blue = secondary;
    }
    var match = brightness - chroma;
    return [
      Math.round((red + match) * 127),
      Math.round((green + match) * 127),
      Math.round((blue + match) * 127)
    ];
  }

  function exquisHuePalettePayload(scale) {
    var payload = [EXQUIS_PALETTE_OFF, 0x00, 0x00, 0x00];
    for (var reservedIndex = EXQUIS_PALETTE_OFF + 1; reservedIndex < EXQUIS_PALETTE_HUE_START; reservedIndex++) {
      payload.push(0x00, 0x00, 0x00);
    }
    for (var interval = 0; interval < 12; interval++) {
      var rgb = hueToExquisRgb(intervalHue(interval, scale), 0.75);
      payload.push(rgb[0], rgb[1], rgb[2]);
    }
    var rootRgb = hueToExquisRgb(SCALE_HUE_ROOT, 1);
    payload.push(rootRgb[0], rootRgb[1], rootRgb[2]);
    return payload;
  }

  function lightFramePaletteRgb(pad, scale) {
    return hueToExquisRgb(intervalHue(pad.interval, scale), pad.isRoot ? 1 : 0.75);
  }

  function lightFrameMeridianPosition(cell, cells) {
    var minX = Infinity;
    var maxX = -Infinity;
    var minY = Infinity;
    var maxY = -Infinity;
    for (var i = 0; i < cells.length; i++) {
      minX = Math.min(minX, cells[i].x);
      maxX = Math.max(maxX, cells[i].x);
      minY = Math.min(minY, cells[i].y);
      maxY = Math.max(maxY, cells[i].y);
    }
    return {
      axisDistance: Math.abs(cell.y - (minY + maxY) / 2),
      crossAxisDistance: Math.abs(cell.x - (minX + maxX) / 2)
    };
  }

  function canonicalLightCellIdsByMidi(cells) {
    var candidatesByMidi = {};
    cells.forEach(function(cell) {
      (candidatesByMidi[cell.midi] || (candidatesByMidi[cell.midi] = [])).push(cell);
    });
    return Object.keys(candidatesByMidi).reduce(function(canonicalByMidi, midi) {
      var candidates = candidatesByMidi[midi];
      candidates.sort(function(a, b) {
        var aPosition = lightFrameMeridianPosition(a, cells);
        var bPosition = lightFrameMeridianPosition(b, cells);
        return aPosition.axisDistance - bPosition.axisDistance || aPosition.crossAxisDistance - bPosition.crossAxisDistance || a.id.localeCompare(b.id);
      });
      canonicalByMidi[midi] = cellKey(candidates[0]);
      return canonicalByMidi;
    }, {});
  }

  function buildPadLightFrame(cells, options) {
    var scale = options.scale;
    var targetByKey = options.targetByKey || {};
    var pathById = options.pathById || {};
    var litPracticeById = options.litPracticeById || {};
    var targetOrderByKey = options.targetOrderByKey || {};
    var pathIndexById = options.pathIndexById || {};
    var pathMidiById = options.pathMidiById || {};
    var fingerById = options.fingerById || {};
    var canonicalCellIdByMidi = canonicalLightCellIdsByMidi(cells);
    var targetByMidi = {};
    var targetOrderByMidi = {};
    var pathByMidi = {};
    var practiceByMidi = {};
    var pathIndexByMidi = {};
    var pathMidiByMidi = {};
    var fingerByMidi = {};
    cells.forEach(function(cell) {
      var cellId = cellKey(cell);
      var key = cellId + ':' + cell.midi;
      if (targetByKey[key]) targetByMidi[cell.midi] = true;
      if (targetOrderByKey[key]) targetOrderByMidi[cell.midi] = targetOrderByKey[key];
      if (pathById[cellId]) pathByMidi[cell.midi] = true;
      if (litPracticeById[cellId]) practiceByMidi[cell.midi] = true;
      if (typeof pathIndexById[cellId] === 'number') pathIndexByMidi[cell.midi] = pathIndexById[cellId];
      if (typeof pathMidiById[cellId] === 'number') pathMidiByMidi[cell.midi] = pathMidiById[cellId];
      if (fingerById[cellId]) fingerByMidi[cell.midi] = fingerById[cellId];
    });
    return cells.map(function(cell) {
      var cellId = cell.id.replace('-octave', '');
      var isCanonical = canonicalCellIdByMidi[cell.midi] === cellId;
      var heldInfo = getHeldInfoForCell(cell);
      var isTarget = isCanonical && !!targetByMidi[cell.midi];
      var isRoot = isCanonical && cell.pc === state.tonicPc;
      var isPath = isCanonical && !!pathByMidi[cell.midi];
      var isScale = options.isPractice && options.view === 'practice'
        ? isPath
        : (isCanonical && isScalePc(cell.pc, scale));
      var isHardwareLit = isCanonical && options.isPractice && options.view === 'practice' && !!practiceByMidi[cell.midi];
      var isMismatch = !!state.mismatched[cellId];
      var role = isMismatch ? 'mismatch'
        : (heldInfo.level > 0 ? 'held'
          : (isTarget ? 'target'
            : (isRoot ? 'root'
              : (isPath ? 'path'
                : ((isScale || isHardwareLit) ? 'scale' : 'off')))));
      return {
        cellId: cellId,
        midi: cell.midi,
        pc: cell.pc,
        padId: exquisLegacyPadId(cell),
        interval: mod(cell.pc - state.tonicPc, 12),
        hue: intervalHue(cell.pc - state.tonicPc, scale),
        role: role,
        isCanonical: isCanonical,
        isRoot: isRoot,
        isScale: isScale || isHardwareLit,
        isHardwareLit: isHardwareLit,
        isPath: isPath,
        pathIndex: isCanonical && isPath ? pathIndexByMidi[cell.midi] : undefined,
        pathMidi: isCanonical && isPath ? pathMidiByMidi[cell.midi] : undefined,
        finger: isCanonical && isPath ? fingerByMidi[cell.midi] : '',
        isTarget: isTarget,
        targetIndex: isCanonical && isTarget ? targetOrderByMidi[cell.midi] : 0,
        isHeld: heldInfo.level > 0,
        isMismatch: isMismatch
      };
    });
  }

  function lightFrameByCellMidi(frame) {
    return frame.reduce(function(index, pad) {
      index[pad.cellId + ':' + pad.midi] = pad;
      return index;
    }, {});
  }

  function expectedCell() {
    var event = expectedExerciseEvent();
    if (!event || !event.targets.length) return null;
    var target = event.targets[0];
    for (var i = 0; i < currentPath.length; i++) {
      var cell = currentPath[i];
      if (cellKey(cell) === target.cellId && cell.midi === target.midi) return cell;
    }
    return null;
  }

  function expectedExerciseEvent() {
    if (!currentExerciseEvents.length) return null;
    return currentExerciseEvents[mod(state.step, currentExerciseEvents.length)];
  }

  function getPromptMidis(event) {
    if (!event) return [];
    if (event.musicalIntent && Array.isArray(event.musicalIntent.promptMidis)) return event.musicalIntent.promptMidis.slice();
    return (event.targets || []).map(function(target) { return target.midi; });
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
    var practicePath = document.querySelector('[data-testid="practice-path-strip"]');
    var practicePathBox = practicePath && practicePath.getBoundingClientRect ? practicePath.getBoundingClientRect() : null;
    var contentTop = practicePathBox && practicePathBox.bottom > headerBox.bottom ? practicePathBox.bottom : headerBox.bottom;
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
    var dashboard = document.querySelector('[data-testid="practice-dashboard"]');
    var dashboardWidth = dashboard && dashboard.offsetParent ? dashboard.getBoundingClientRect().width + 16 : 0;
    if (state.orientation === 'horizontal') {
      return {
        width: Math.max(0, stageBox.width - topWidth - bottomWidth - 44),
        height: Math.max(0, safeBottom - contentTop - 26)
      };
    }
    return {
      width: Math.max(0, stageBox.width - 20 - dashboardWidth),
      height: Math.max(0, safeBottom - contentTop - topHeight - bottomHeight - 66)
    };
  }

  function getKeyboardScale(baseWidth, baseHeight) {
    var available = getKeyboardAvailableSpace();
    if (!available.width || !available.height) return 1;
    var minScale = state.orientation === 'vertical' ? 0.52 : 0.72;
    var maxScale = state.workspace === 'practice' && state.orientation === 'horizontal' ? 2.5 : 1.9;
    return Math.max(minScale, Math.min(maxScale, available.width / baseWidth, available.height / baseHeight));
  }

  function findCellsByMidi(cells, midi) {
    return cells.filter(function(cell) { return cell.midi === midi; });
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

  function describeCoachAction(event, current, finger, gripAssignments) {
    if (state.mode !== 'practice') return 'Play freely across the full Exquis surface.';
    if (event && event.type === 'grip') {
      var gripFingers = (gripAssignments || []).map(function(assignment) {
        return String(assignment.finger);
      }).join(', ');
      return 'Press every highlighted button together' + (gripFingers ? '. Chord positions: ' + gripFingers + '.' : '.');
    }
    if (!current) return 'Choose a lesson target to begin.';
    return 'Press the highlighted ' + noteLabelFromMidi(current.midi) + ' with ' + fingerDisplayName(finger) + '.';
  }

  function gripFingerAssignments(event) {
    if (!event || !event.fingering) return [];
    var selected = (event.fingering.alternatives || []).filter(function(option) {
      return option.id === state.gripFingeringOption;
    })[0];
    return selected ? selected.assignments : (event.fingering.assignments || []);
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
      if (held && held.midi === cell.midi && ((held.cellIds && held.cellIds.indexOf(cell.id) >= 0) || held.cellId === cell.id)) {
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
    if (held && ageMs >= 0 && ageMs < EXQUIS_MIN_MIDI_HOLD_MS && !pendingShortNoteReleases[key] && !isPendingReleaseStrumArticulation(key)) {
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
    forgetChannelHeldNote(channel, midi);
    recentMidiNoteOffs[rawMidi] = Date.now();
    if (held) {
      logEvent('midi', 'note-off release input ' + noteLabelFromMidi(midi) + ' age=' + Math.round(ageMs) + 'ms velocity=' + Math.round(held.velocity || 0) + ' currentPressure=' + Math.round(held.pressure || 0) + ' peakPressure=' + Math.round(held.peakPressure || 0) + ' channel=' + (channel + 1));
    }
    releaseMidiVoice(key, false, held);
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
    held.peakPressure = Math.max(held.peakPressure || 0, held.pressure);
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

  function isReleaseStrumContactNoise(velocity) {
    if (velocity > 2) return false;
    var articulation = selectedArticulation();
    return articulation && articulation.family === 'plucked' && articulation.onsetMode === 'release-strum';
  }

  function scoreSinglePracticeNote(expected, expectedKey, midi) {
    var advanced = false;
    if (expected && mod(midi, 12) === expected.pc) {
      state.correctCount += 1;
      state.streak += 1;
      recordRepertoireLoop(expectedExerciseEvent());
      state.calibrated[expectedKey] = { expectedMidi: expected.midi, receivedMidi: midi, at: state.lastMidiAt };
      delete state.mismatched[expectedKey];
      setFeedback('Correct: ' + noteLabelFromMidi(midi) + ' matches the current target.', 'good');
      if (state.autoAdvance) {
        state.step += 1;
        advanced = true;
      }
    } else if (expected) {
      state.missCount += 1;
      state.streak = 0;
      state.mismatched[expectedKey] = { expectedMidi: expected.midi, receivedMidi: midi, at: state.lastMidiAt };
      setFeedback('Not this one: heard ' + noteLabelFromMidi(midi) + ', target is ' + noteLabelFromMidi(expected.midi) + '.', 'bad');
    }
    return advanced;
  }

  function resolvePendingGripAttempt(event) {
    if (!pendingGripAttempts || pendingGripAttempts.eventId !== event.id) return;
    if (pendingGripTimer) window.clearTimeout(pendingGripTimer);
    pendingGripTimer = null;
    var result = evaluateGripAttempt(event, pendingGripAttempts.attempts);
    pendingGripAttempts = null;
    var advanced = false;
    if (result.accepted) {
      state.correctCount += 1;
      state.streak += 1;
      recordRepertoireLoop(event);
      var declaredOption = event.fingering.alternatives.filter(function(option) { return option.id === state.gripFingeringOption; })[0];
      setFeedback('Correct grip: ' + event.targets.map(function(target) { return noteLabelFromMidi(target.midi); }).join(' + ') + '.' + (declaredOption ? ' Declared ' + declaredOption.label + ' fingering.' : ''), 'good');
      if (state.autoAdvance) {
        state.step += 1;
        advanced = true;
      }
    } else {
      state.missCount += 1;
      state.streak = 0;
      var detail = result.outcome === 'late' ? 'played too far apart' : (result.outcome === 'wrong' ? 'includes a wrong note' : 'is missing ' + result.missing.map(function(target) { return noteLabelFromMidi(target.midi); }).join(' + '));
      setFeedback('Grip not accepted: ' + detail + '.', 'bad');
    }
    render();
    if (advanced) syncExquisPracticePadFrame();
  }

  function queueGripPracticeNote(event, attempt) {
    if (!pendingGripAttempts || pendingGripAttempts.eventId !== event.id) {
      pendingGripAttempts = { eventId: event.id, attempts: [] };
      if (pendingGripTimer) window.clearTimeout(pendingGripTimer);
      pendingGripTimer = window.setTimeout(function() { resolvePendingGripAttempt(event); }, (event.timing.toleranceMs || 80) + GRIP_COLLECTION_GRACE_MS);
    }
    pendingGripAttempts.attempts.push(attempt);
    var result = evaluateGripAttempt(event, pendingGripAttempts.attempts);
    if (result.accepted) resolvePendingGripAttempt(event);
  }

  function handleMidiNote(rawMidi, velocity, channel) {
    var midi = displayMidiFromRaw(rawMidi);
    if (isReleaseBounceNoteOn(rawMidi, velocity)) {
      logEvent('midi', 'note-on ignored release bounce ' + noteLabelFromMidi(midi) + ' midi=' + midi + ' raw=' + rawMidi + ' velocity=' + velocity + ' channel=' + (channel + 1));
      return;
    }
    if (isReleaseStrumContactNoise(velocity)) {
      logEvent('midi', 'note-on ignored release-strum contact noise ' + noteLabelFromMidi(midi) + ' midi=' + midi + ' raw=' + rawMidi + ' velocity=' + velocity + ' channel=' + (channel + 1));
      return;
    }
    cancelPendingReleaseStrumCommitsForContact(midi);
    dampReleasedPluckedOneShotsForSamePitchContact(midi);
    forgetInactiveReleasedPluckedOneShotsForNewContact();
    if (window.__exquisLatencyProbe && Array.isArray(window.__exquisLatencyProbe.inputs)) {
      window.__exquisLatencyProbe.inputs.push({ midi: midi, at: Date.now() });
    }
    var cells = makeGrid();
    var expected = expectedCell();
    var expectedKey = cellKey(expected);
    var matchingCells = findCellsByMidi(cells, midi);
    // MIDI identifies a physical pad only when this pitch has one visual alias.
    // Duplicate pads are intentionally recorded as pitch-only hardware evidence.
    var hitCell = matchingCells.length === 1 ? matchingCells[0] : null;
    var matchingCellIds = {};
    matchingCells.forEach(function(cell) { matchingCellIds[cell.id] = true; });
    state.lastMidi = {
      midi: midi,
      velocity: velocity,
      cellId: hitCell ? hitCell.id : '',
      cellIds: matchingCells.map(function(cell) { return cell.id; })
    };
    state.activeMidiCellId = hitCell ? hitCell.id : '';
    state.activeMidiCellIds = matchingCellIds;
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
    releaseDuplicateMidiVoices(midi, heldKey);
    state.heldNotes[heldKey] = {
      midi: midi,
      rawMidi: rawMidi,
      pc: mod(midi, 12),
      velocity: velocity,
      pressure: velocity,
      peakPressure: velocity,
      cellId: hitCell ? hitCell.id : '',
      cellIds: matchingCells.map(function(cell) { return cell.id; }),
      channel: channel,
      startedAt: Date.now()
    };
    rememberChannelHeldNote(channel, midi);
    scheduleMidiVoiceStart(heldKey, midi, velocity, hitCell ? hitCell.id : '', channel);
    updateSsliExpressionFromHeldNotes();
    logEvent('midi', 'note-on ' + noteLabelFromMidi(midi) + ' midi=' + midi + ' raw=' + rawMidi + ' velocity=' + velocity + ' channel=' + (channel + 1) + ' match=' + (hitCell ? hitCell.id : 'pitch-only') + ' aliases=' + (matchingCells.length ? matchingCells.map(function(cell) { return cell.id; }).join('|') : 'none') + ' ' + midiCellDebug(hitCell));
    rememberRecentMidiChordNote(midi, velocity, channel, hitCell);

    var expectedEvent = expectedExerciseEvent();
    if (state.mode !== 'practice') {
      setFeedback('Play mode: ' + noteLabelFromMidi(midi) + ' is sounding freely.', 'live');
    } else if (expectedEvent && expectedEvent.type === 'grip') {
      queueGripPracticeNote(expectedEvent, { midi: midi, cellId: hitCell ? hitCell.id : '', at: state.lastMidiAt });
    } else {
      var advancedPracticeStep = scoreSinglePracticeNote(expected, expectedKey, midi);
    }

    if (midiHitTimer) window.clearTimeout(midiHitTimer);
    midiHitTimer = window.setTimeout(function() {
      state.activeMidiCellId = '';
      state.activeMidiCellIds = {};
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
    var developerPadCell = channel === 15 ? makeGrid().find(function(cell) { return exquisLegacyPadId(cell) === midi; }) : null;
    if (developerPadCell && isNoteOn) {
      handleMidiNote(developerPadCell.midi, velocity, channel);
    } else if (developerPadCell && isNoteOff) {
      releaseMidiNote(developerPadCell.midi, channel);
    } else if (developerPadCell && status === 0xA0) {
      updateMidiPressure(developerPadCell.midi, velocity, 'poly-aftertouch', channel);
    } else if (isNoteOn) {
      handleMidiNote(midi, velocity, channel);
    } else if (isNoteOff) {
      releaseMidiNote(midi, channel);
    } else if (status === 0xA0) {
      updateMidiPressure(displayMidiFromRaw(midi), velocity, 'poly-aftertouch', channel);
    } else if (status === 0xD0) {
      channelHeldMidiNotes(channel).forEach(function(channelMidi) {
        updateMidiPressure(channelMidi, midi, 'channel-pressure', channel);
      });
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

  function sendMidiLocalSoundOff(reason) {
    if (!midiOutput || !midiOutput.send) return false;
    try {
      for (var channel = 0; channel < 16; channel++) {
        var status = 0xB0 | channel;
        // Prevent the hardware/output device from also sounding its own patch
        // while the exhibit renders the selected SSLI instrument.
        midiOutput.send([status, 122, 0]); // Local Control Off
        midiOutput.send([status, 120, 0]); // All Sound Off
        midiOutput.send([status, 123, 0]); // All Notes Off
      }
      logEvent('midi', 'sent MIDI local-control/all-sound-off sweep' + (reason ? ' after ' + reason : ''));
      return true;
    } catch (err) {
      logEvent('midi', 'MIDI local sound-off failed: ' + (err && err.message ? err.message : err));
      return false;
    }
  }

  function connectMidiOutput(output) {
    midiOutput = output || null;
    if (midiOutput) {
      state.selectedMidiOutputId = midiOutput.id || '';
      logEvent('midi', 'output ready ' + midiDeviceLabel(midiOutput) + ' id=' + (midiOutput.id || 'unknown'));
      sendMidiLocalSoundOff('output connect');
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

  function sendOfficialSettingsDeveloperMode(enabled, reason) {
    var mask = EXQUIS_DEVELOPER_PADS_MASK | EXQUIS_DEVELOPER_SETTINGS_SOUND_MASK;
    return sendRawMidi(buildExquisSysex(0x00, [enabled ? mask : 0x00]), 'Exquis sync send ' + reason);
  }

  function sendOfficialDialListenDeveloperMode(enabled, reason) {
    return sendRawMidi(buildExquisSysex(0x00, [enabled ? EXQUIS_DEVELOPER_DIAL_LISTEN_MASK : 0x00]), 'Exquis sync send ' + reason);
  }

  function beginOfficialKeyModeTransaction(reason) {
    return sendOfficialPadsDeveloperMode(true, (reason || 'native-keymode') + ' developer-mode pads=0x01');
  }

  function endOfficialKeyModeTransaction(reason) {
    if (state.exquisSyncEnabled || state.exquisDialListenEnabled) return true;
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
    window.setTimeout(function() { sendRawMidi(buildExquisSysex(0x06, [rootPc]), 'Exquis native probe root=' + getTonicName() + ' ' + label); }, EXQUIS_KEY_MODE_COMMAND_GAP_MS);
    window.setTimeout(function() { sendRawMidi(buildExquisSysex(0x07, [scaleIndex]), 'Exquis native probe scale=' + state.scaleId + ' index=' + scaleIndex + ' ' + label); }, EXQUIS_KEY_MODE_COMMAND_GAP_MS * 2);
    window.setTimeout(function() { sendRawMidi(buildExquisSysex(0x03, []), 'Exquis native probe refresh ' + label); }, EXQUIS_KEY_MODE_COMMAND_GAP_MS * 3);
    window.setTimeout(function() { sendRawMidi(buildExquisSysex(0x06, []), 'Exquis native probe root-readback ' + label); }, EXQUIS_KEY_MODE_COMMAND_GAP_MS * 4);
    window.setTimeout(function() { sendRawMidi(buildExquisSysex(0x07, []), 'Exquis native probe scale-readback ' + label); }, EXQUIS_KEY_MODE_COMMAND_GAP_MS * 5);
    window.setTimeout(function() { sendRawMidi(buildExquisSysex(0x00, [0x00]), 'Exquis native probe developer-mode off ' + label); }, EXQUIS_KEY_MODE_COMMAND_GAP_MS * 6);
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
    }, 250);
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

  function probeExquisRgbPad() {
    if (!midiOutput || !midiOutput.send) {
      state.exquisSyncStatus = 'RGB pad test: no MIDI output';
      render();
      return;
    }
    cancelPendingExquisKeyModeSync();
    sendRawMidi(buildExquisSysex(0x00, [EXQUIS_DEVELOPER_PADS_MASK]), 'Exquis official RGB pad test developer-mode pads=0x01');
    window.setTimeout(function() {
      sendRawMidi(buildExquisSysex(0x04, [0, 0x7F, 0x00, 0x7F, 0x00]), 'Exquis official RGB pad test pad=0 magenta');
      state.exquisSyncStatus = 'Official pad color test active: bottom-left pad is magenta';
      logEvent('midi', 'Official RGB pad test sent one Developer Mode direct LED color write for pad=0 RGB=127,0,127 fx=0; edge controls remain native');
      render();
    }, EXQUIS_KEY_MODE_COMMAND_GAP_MS);
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
    }, masks.length * 900 + EXQUIS_KEY_MODE_COMMAND_GAP_MS * 7);
    render();
  }

  function sendExquisRoot() {
    return sendExquisSysex(0x06, [mod(state.tonicPc, 12)], 'root=' + getTonicName());
  }

  function sendExquisScale() {
    return sendExquisSysex(0x01, [1], 'custom-scale-list count=1');
  }

  function selectExquisCustomScale() {
    return sendExquisSysex(0x07, [0], 'custom-scale-index=0');
  }

  function sendExquisCustomScaleDegrees() {
    var degrees = scaleDegreesFor(state.scaleId);
    return sendExquisSysex(0x08, degrees, 'custom-scale=' + state.scaleId + ' degrees=' + degrees.join(','));
  }

  function scheduleExquisPadColors(delayMs) {
    var pads = currentLightFrame.slice().sort(function(a, b) { return a.padId - b.padId; });
    if (!pads.length) {
      pads = buildPadLightFrame(makeGrid(), {
        scale: getScale(),
        isPractice: state.mode === 'practice',
        view: state.view
      }).sort(function(a, b) { return a.padId - b.padId; });
    }
    logEvent('midi', 'Exquis sync send pad-colors root=' + getTonicName() + ' scale=' + state.scaleId + ' count=' + pads.length);
    scheduleExquisKeyModeSync(function() {
      sendExquisSysex(0x02, exquisHuePalettePayload(getScale()), 'pad-palette off/root-relative-hues');
    }, delayMs);
    pads.forEach(function(pad, index) {
      var paletteIndex = lightFramePaletteIndex(pad);
      scheduleExquisKeyModeSync(function() {
        sendRawMidi([0xBF, pad.padId, paletteIndex], '');
        lastExquisPadPalette[pad.padId] = paletteIndex;
      }, delayMs + (index + 1) * EXQUIS_LED_COMMAND_GAP_MS);
    });
    pads.forEach(function(pad, index) {
      var effect = lightFrameEffect(pad);
      scheduleExquisKeyModeSync(function() {
        sendRawMidi([0xAF, pad.padId, effect], '');
        lastExquisPadEffect[pad.padId] = effect;
      }, delayMs + (pads.length + index + 1) * EXQUIS_LED_COMMAND_GAP_MS);
    });
  }

  function lightFramePaletteIndex(pad) {
    return pad.isRoot
      ? EXQUIS_PALETTE_ROOT
      : (pad.isScale
        ? EXQUIS_PALETTE_HUE_START + pad.interval
        : EXQUIS_PALETTE_OFF);
  }

  function lightFrameEffect(pad) {
    return pad.isTarget ? 0x3F : 0x00;
  }

  function syncExquisPracticePadFrame() {
    if (!state.exquisSyncEnabled || !midiOutput || !currentLightFrame.length) return;
    var changedPalettePads = currentLightFrame.filter(function(pad) {
      return lastExquisPadPalette[pad.padId] !== lightFramePaletteIndex(pad);
    });
    var effectPads = currentLightFrame.slice().sort(function(a, b) { return a.padId - b.padId; });
    if (!changedPalettePads.length && !effectPads.length) return;
    logEvent('midi', 'Exquis practice light frame palette-changed=' + changedPalettePads.length + ' effects-refreshed=' + effectPads.length);
    changedPalettePads.sort(function(a, b) { return a.padId - b.padId; }).forEach(function(pad, index) {
      scheduleExquisKeyModeSync(function() {
        var paletteIndex = lightFramePaletteIndex(pad);
        sendRawMidi([0xBF, pad.padId, paletteIndex], '');
        lastExquisPadPalette[pad.padId] = paletteIndex;
      }, (index * 2 + 1) * EXQUIS_LED_COMMAND_GAP_MS);
    });
    effectPads.forEach(function(pad, index) {
      scheduleExquisKeyModeSync(function() {
        var effect = lightFrameEffect(pad);
        sendRawMidi([0xAF, pad.padId, effect], '');
        lastExquisPadEffect[pad.padId] = effect;
      }, (changedPalettePads.length * 2 + index + 1) * EXQUIS_LED_COMMAND_GAP_MS);
    });
  }

  function requestExquisReadback() {
    var okRoot = sendExquisSysex(0x06, [], 'request-root-readback');
    var okScale = sendExquisSysex(0x07, [], 'request-scale-readback');
    return okRoot && okScale;
  }

  function refreshExquisDisplay(reason) {
    return sendExquisSysex(0x03, [], reason || 'refresh-display');
  }

  function cancelPendingExquisKeyModeSync() {
    exquisKeyModeSyncTimers.forEach(function(timer) { window.clearTimeout(timer); });
    exquisKeyModeSyncTimers = [];
  }

  function scheduleExquisKeyModeSync(callback, delayMs) {
    var timer = window.setTimeout(function() {
      exquisKeyModeSyncTimers = exquisKeyModeSyncTimers.filter(function(candidate) { return candidate !== timer; });
      callback();
    }, delayMs);
    exquisKeyModeSyncTimers.push(timer);
  }

  function syncExquisKeyModeToHardware() {
    if (!state.exquisSyncEnabled) return;
    cancelPendingExquisKeyModeSync();
    lastExquisPadPalette = {};
    lastExquisPadEffect = {};
    beginOfficialKeyModeTransaction('key/mode sync');
    state.exquisCustomScaleActive = true;
    scheduleExquisKeyModeSync(sendExquisRoot, EXQUIS_KEY_MODE_COMMAND_GAP_MS);
    scheduleExquisKeyModeSync(sendExquisScale, EXQUIS_KEY_MODE_COMMAND_GAP_MS * 2);
    scheduleExquisKeyModeSync(selectExquisCustomScale, EXQUIS_KEY_MODE_COMMAND_GAP_MS * 3);
    scheduleExquisKeyModeSync(sendExquisCustomScaleDegrees, EXQUIS_KEY_MODE_COMMAND_GAP_MS * 4);
    var refreshDelay = EXQUIS_KEY_MODE_COMMAND_GAP_MS * 5;
    scheduleExquisKeyModeSync(function() { refreshExquisDisplay('refresh-before-pad-colors'); }, refreshDelay);
    var ledStartDelay = EXQUIS_KEY_MODE_COMMAND_GAP_MS * 6;
    scheduleExquisPadColors(ledStartDelay);
    var afterLedFrameDelay = ledStartDelay + EXQUIS_LED_COMMAND_GAP_MS * (EXQUIS_PAD_COUNT * 2 + 1);
    scheduleExquisKeyModeSync(function() { sendExquisSysex(0x06, [], 'request-root-readback'); }, afterLedFrameDelay + EXQUIS_KEY_MODE_COMMAND_GAP_MS);
    scheduleExquisKeyModeSync(function() { sendExquisSysex(0x07, [], 'request-scale-readback'); }, afterLedFrameDelay + EXQUIS_KEY_MODE_COMMAND_GAP_MS * 2);
    scheduleExquisKeyModeSync(function() { endOfficialKeyModeTransaction('key/mode sync'); }, afterLedFrameDelay + EXQUIS_KEY_MODE_COMMAND_GAP_MS * 3);
    state.exquisSyncStatus = 'Exquis sync: active ' + getTonicName() + ' ' + getScale().name + ' custom scale';
    render();
  }

  function syncExquisKeyModeFromUiChange() {
    if (!state.exquisSyncEnabled) return;
    exquisUserKeyModeAuthorityUntil = Date.now() + 1400;
    syncExquisKeyModeToHardware();
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
      if (state.exquisCustomScaleActive && parsed.payload[0] === 0) {
        logEvent('midi', 'Exquis custom scale index=' + parsed.payload[0] + ' retained as ' + state.scaleId);
      } else {
        updateScaleFromHardwareNumber(parsed.payload[0], 'official SysEx');
      }
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
    startExquisLegacyKeepalive();
    syncExquisKeyModeToHardware();
  }

  function disableExquisSync() {
    cancelPendingExquisKeyModeSync();
    lastExquisPadPalette = {};
    lastExquisPadEffect = {};
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
    state.exquisCustomScaleActive = false;
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

  function renderExerciseOptions() {
    clearChildren(els.exercise);
    if (els.exerciseButtons) clearChildren(els.exerciseButtons);
    var exercises = exercisesForSelectedFamily();
    if (!exercises.some(function(exercise) { return exercise.id === state.exerciseId; })) {
      state.exerciseId = exercises.length ? exercises[0].id : EXERCISES[0].id;
    }
    applyCanonicalProgressionScale();
    for (var i = 0; i < exercises.length; i++) {
      var exercise = exercises[i];
      var eo = document.createElement('option');
      eo.value = exercise.id;
      eo.textContent = exercise.name;
      els.exercise.appendChild(eo);
      if (els.exerciseButtons) {
        var eb = document.createElement('button');
        eb.type = 'button';
        eb.className = 'exercise-button';
        eb.dataset.value = exercise.id;
        eb.setAttribute('data-testid', 'exercise-button-' + exercise.id);
        eb.textContent = exerciseButtonLabel(exercise);
        eb.setAttribute('aria-label', exercise.name + ': ' + exercise.prompt);
        els.exerciseButtons.appendChild(eb);
      }
    }
    els.exercise.value = state.exerciseId;
  }

  function progressionGenreOptions() {
    return [{ id: 'starter', name: 'Starter repertoire' }].concat(SSLI_PROGRESSION_GROUPS.map(function(group, index) {
      return { id: 'ssli-' + index, name: group.genre };
    }));
  }

  function exercisesForSelectedFamily() {
    if (state.exerciseFamily === 'repertoire') {
      return REPERTOIRE_LESSONS.map(function(lesson) {
        return {
          id: lesson.id,
          name: lesson.name,
          family: 'repertoire',
          prompt: lesson.style + ' repertoire at ' + String(lesson.tempo) + ' BPM.'
        };
      });
    }
    if (state.exerciseFamily !== 'progressions') {
      return EXERCISES.filter(function(exercise) { return exercise.family === state.exerciseFamily; });
    }
    var sslGenre = /^ssli-(\d+)$/.exec(state.progressionGenre || '');
    if (!sslGenre) return EXERCISES.filter(function(exercise) { return exercise.family === 'progressions'; });
    var genreIndex = parseInt(sslGenre[1], 10);
    var group = SSLI_PROGRESSION_GROUPS[genreIndex];
    if (!group || !Array.isArray(group.progressions)) return EXERCISES.filter(function(exercise) { return exercise.family === 'progressions'; });
    return group.progressions.map(function(progression, progressionIndex) {
      return {
        id: ssliProgressionExerciseId(genreIndex, progressionIndex),
        name: ssliProgressionDisplayName(progression),
        family: 'progressions',
        prompt: group.genre + ': ' + (progression.usage || 'SSLI progression library')
      };
    });
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
    appendOptions(els.exerciseFamily, EXERCISE_FAMILIES, 'id', 'name');
    appendOptions(els.progressionGenre, progressionGenreOptions(), 'id', 'name');
    renderExerciseOptions();
    syncSoundSelectorsFromPreset();
    syncFxSelectorsFromPreset();
    renderSoundSelectorOptions();
    renderFxSelectorOptions();
  }

  function appendInversionOptions(select, noteCount, selected) {
    clearChildren(select);
    for (var inversion = 0; inversion < noteCount; inversion++) {
      var option = document.createElement('option');
      option.value = String(inversion);
      option.textContent = inversion === 0 ? 'Root' : String(inversion) + (inversion === 1 ? 'st' : inversion === 2 ? 'nd' : inversion === 3 ? 'rd' : 'th');
      select.appendChild(option);
    }
    select.value = String(Math.min(noteCount - 1, selected));
  }

  function renderProgressionVoicingControls(events, active) {
    if (!els.progressionVoicingPanel) return;
    els.progressionVoicingPanel.hidden = !active;
    if (!active) return;
    els.progressionGlobalNoteCount.value = String(state.progressionVoicing.noteCount);
    appendInversionOptions(els.progressionGlobalInversion, state.progressionVoicing.noteCount, state.progressionVoicing.inversion);
    clearChildren(els.progressionChordRows);
    events.forEach(function(event, index) {
      var voicing = progressionVoicingForStep(index);
      var row = document.createElement('div');
      row.className = 'progression-chord-row';
      row.setAttribute('data-testid', 'progression-chord-row');
      row.dataset.step = String(index);
      var degree = document.createElement('span'); degree.className = 'progression-chord-degree'; degree.setAttribute('data-testid', 'progression-chord-degree'); degree.textContent = event.musicalIntent.degree;
      var quality = document.createElement('span'); quality.className = 'progression-chord-quality'; quality.textContent = event.musicalIntent.quality;
      var noteLabel = document.createElement('label'); noteLabel.innerHTML = '<span>Notes</span>';
      var noteSelect = document.createElement('select'); noteSelect.setAttribute('data-testid', 'progression-chord-note-count');
      [2, 3, 4, 5].forEach(function(count) { var option = document.createElement('option'); option.value = String(count); option.textContent = String(count); noteSelect.appendChild(option); });
      noteSelect.value = String(voicing.noteCount); noteLabel.appendChild(noteSelect);
      var inversionLabel = document.createElement('label'); inversionLabel.innerHTML = '<span>Inversion</span>';
      var inversionSelect = document.createElement('select'); inversionSelect.setAttribute('data-testid', 'progression-chord-inversion'); appendInversionOptions(inversionSelect, voicing.noteCount, voicing.inversion); inversionLabel.appendChild(inversionSelect);
      row.appendChild(degree); row.appendChild(quality); row.appendChild(noteLabel); row.appendChild(inversionLabel); els.progressionChordRows.appendChild(row);
    });
  }

  function renderRepertoireSectionControls(active) {
    if (!els.repertoireSectionPanel || !els.repertoireSection) return;
    els.repertoireSectionPanel.hidden = !active;
    if (!active) return;
    var selection = selectedRepertoireSection();
    if (!selection) return;
    clearChildren(els.repertoireSection);
    selection.lesson.sections.forEach(function(section) {
      var option = document.createElement('option');
      option.value = section.id;
      option.textContent = section.name;
      els.repertoireSection.appendChild(option);
    });
    els.repertoireSection.value = selection.section.id;
    if (els.repertoireTempo) els.repertoireTempo.value = String(repertoireTempo(selection));
    var completedLoops = repertoireCompletedLoopCount(selection);
    if (els.repertoireSectionSummary) {
      var chordCount = 0;
      els.repertoireSectionSummary.textContent = selection.section.name + ' · ' + selection.lesson.style + ' · ' + String(selection.lesson.tempo) + ' BPM · loops after ' + String(chordCount) + ' chords';
    }
    if (els.repertoireSectionSummary) {
      els.repertoireSectionSummary.textContent = selection.section.name + ' · ' + String(repertoireTempo(selection)) + ' BPM · ' + String(completedLoops) + ' completed loop' + (completedLoops === 1 ? '' : 's');
    }
  }

  function render() {
    var logicCells = makeGrid();
    var cells = logicCells;
    var scale = getScale();
    var strategy = getStrategy();
    var exercise = getExercise();
    var fingers = getStrategyFingers(strategy);
    var isPracticeMode = state.mode === 'practice';
    var progressionPractice = isPracticeMode && state.exerciseFamily === 'progressions';
    var repertoirePractice = isPracticeMode && state.exerciseFamily === 'repertoire';
    var chordPractice = progressionPractice || repertoirePractice;
    renderRootOptions(logicCells);
    if (els.tonic) els.tonic.value = String(state.tonicPc);
    if (els.scale) els.scale.value = state.scaleId;
    if (els.strategy) els.strategy.value = state.strategyId;
    if (els.hand) els.hand.value = state.hand;
    if (els.exercise) els.exercise.value = state.exerciseId;
    if (els.octave) els.octave.value = state.octaveSide;
    if (els.view) els.view.value = state.view;
    var legacyPath = getPracticePath(logicCells, scale);
    currentExerciseEvents = buildPracticeExerciseEvents(legacyPath, fingers);
    currentPath = currentExerciseEvents.reduce(function(cells, event) {
      return cells.concat(event.sourceCells || (event.sourceCell ? [event.sourceCell] : []));
    }, []);
    var currentEvent = expectedExerciseEvent();
    var concealExerciseTargets = !!(isPracticeMode && currentEvent && currentEvent.musicalIntent && currentEvent.musicalIntent.concealTargets);
    var path = concealExerciseTargets || chordPractice ? [] : currentPath;
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

    state.step = currentExerciseEvents.length ? mod(state.step, currentExerciseEvents.length) : 0;
    var currentStepIndex = state.step;
    currentEvent = expectedExerciseEvent();
    var currentGripTargetsByKey = {};
    var currentGripFingerByCell = {};
    var currentGripTargetNotes = [];
    var currentTargetByKey = {};
    if (isPracticeMode && currentEvent && currentEvent.targets) {
      currentEvent.targets.forEach(function(target) {
        currentTargetByKey[target.cellId + ':' + target.midi] = true;
      });
    }
    if (isPracticeMode && currentEvent && currentEvent.type === 'grip') {
      currentEvent.targets.forEach(function(target, index) {
        currentGripTargetsByKey[target.cellId + ':' + target.midi] = index + 1;
        currentGripTargetNotes.push(noteLabelFromMidi(target.midi));
      });
      gripFingerAssignments(currentEvent).forEach(function(assignment) {
        currentGripFingerByCell[assignment.cellId] = assignment.finger;
      });
    }
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
    if (els.appShell) {
      els.appShell.setAttribute('data-mode', state.mode);
      els.appShell.setAttribute('data-workspace', state.workspace);
    }
    if (els.libraryWorkspace) els.libraryWorkspace.hidden = state.workspace !== 'library';
    if (els.studioWorkspace) els.studioWorkspace.hidden = state.workspace !== 'studio';
    if (els.setupWorkspace) els.setupWorkspace.hidden = state.workspace !== 'setup';
    if (els.sidePanel) els.sidePanel.hidden = state.workspace !== 'practice' || !state.coachOpen;
    if (els.coachToggle) {
      els.coachToggle.hidden = state.workspace !== 'practice';
      els.coachToggle.setAttribute('aria-expanded', state.coachOpen ? 'true' : 'false');
      els.coachToggle.textContent = state.coachOpen ? 'Close coach' : 'Coach';
    }
    if (els.connectionGate) els.connectionGate.hidden = !state.launchGateOpen;
    if (els.studioControlsSlot) {
      els.studioControlsSlot.setAttribute('data-studio-tab', state.studioTab);
      els.studioControlsSlot.setAttribute('data-sound-tab', state.soundTab);
    }
    if (els.studioTabs) {
      var studioTabButtons = els.studioTabs.querySelectorAll('button[data-studio-tab]');
      for (var studioTabIndex = 0; studioTabIndex < studioTabButtons.length; studioTabIndex++) {
        var studioTabButton = studioTabButtons[studioTabIndex];
        var studioTabActive = studioTabButton.dataset.studioTab === state.studioTab;
        studioTabButton.classList.toggle('active', studioTabActive);
        studioTabButton.setAttribute('aria-pressed', studioTabActive ? 'true' : 'false');
      }
    }
    if (els.soundTabs) {
      els.soundTabs.hidden = state.workspace !== 'studio' || state.studioTab !== 'sound';
      var soundTabButtons = els.soundTabs.querySelectorAll('button[data-sound-tab]');
      for (var soundTabIndex = 0; soundTabIndex < soundTabButtons.length; soundTabIndex++) {
        var soundTabButton = soundTabButtons[soundTabIndex];
        var soundTabActive = soundTabButton.dataset.soundTab === state.soundTab;
        soundTabButton.classList.toggle('active', soundTabActive);
        soundTabButton.setAttribute('aria-pressed', soundTabActive ? 'true' : 'false');
      }
    }
    if (els.studioTitle) els.studioTitle.textContent = state.studioTab === 'sound' ? 'Shape your sound.' : 'Connect hardware.';
    if (els.studioDescription) els.studioDescription.textContent = state.studioTab === 'sound'
      ? 'Choose the voice, effects, and response curve that make the Exquis feel like your instrument.'
      : 'MIDI routing, Exquis synchronization, and diagnostics live here—not inside a lesson.';
    if (els.workspaceNav) {
      var workspaceButtons = els.workspaceNav.querySelectorAll('button[data-workspace]');
      for (var workspaceIndex = 0; workspaceIndex < workspaceButtons.length; workspaceIndex++) {
        var workspaceButton = workspaceButtons[workspaceIndex];
        var workspaceActive = workspaceButton.dataset.workspace === state.workspace;
        workspaceButton.classList.toggle('active', workspaceActive);
        workspaceButton.setAttribute('aria-pressed', workspaceActive ? 'true' : 'false');
      }
    }
    if (els.exquisDevice) {
      els.exquisDevice.setAttribute('data-orientation', state.orientation);
      els.exquisDevice.setAttribute('data-rotation', String(mod(state.rotation, 360)));
    }
    els.keyboard.className = 'keyboard keyboard-' + state.orientation + (state.rotation === 90 || state.rotation === 270 ? ' keyboard-rotated-sideways' : '');
    els.keyboard.setAttribute('data-mode', state.mode);
    els.keyboard.setAttribute('data-rotation', String(mod(state.rotation, 360)));
    renderEdgeControls();
    var baseFieldBounds = getFieldBounds(logicCells);
    var compactPracticeSurface = state.workspace === 'practice' && state.orientation === 'horizontal';
    var baseKeyboardWidth = Math.round(baseFieldBounds.width + (compactPracticeSurface ? 0 : 130));
    var baseKeyboardHeight = Math.round(baseFieldBounds.height + (compactPracticeSurface ? 0 : 48));
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
    var currentGripCells = cells.filter(function(cell) { return !!currentGripTargetsByKey[cell.id + ':' + cell.midi]; });
    if (currentGripCells.length > 1) {
      var keyWidth = CELL_W * layoutScale;
      var keyHeight = CELL_H * layoutScale;
      var minTargetX = Math.min.apply(null, currentGripCells.map(function(cell) { return cell.x + shiftX - keyWidth / 2; }));
      var maxTargetX = Math.max.apply(null, currentGripCells.map(function(cell) { return cell.x + shiftX + keyWidth / 2; }));
      var minTargetY = Math.min.apply(null, currentGripCells.map(function(cell) { return cell.y + shiftY - keyHeight / 2; }));
      var maxTargetY = Math.max.apply(null, currentGripCells.map(function(cell) { return cell.y + shiftY + keyHeight / 2; }));
      var bracket = document.createElement('div');
      var chordTargetLabel = 'Chord target: press together';
      var bracketLabel = document.createElement('span');
      var progressionDegree = currentEvent.musicalIntent && currentEvent.musicalIntent.degree ? currentEvent.musicalIntent.degree + ' · ' : '';
      bracket.className = 'chord-target-bracket';
      bracket.setAttribute('data-testid', 'chord-target-bracket');
      bracket.setAttribute('role', 'note');
      bracket.setAttribute('aria-label', chordTargetLabel + ' (' + progressionDegree + currentGripTargetNotes.join(' · ') + ')');
      bracket.setAttribute('data-label', progressionDegree + currentGripTargetNotes.join(' · ') + ' together');
      bracketLabel.className = 'chord-target-bracket-label';
      bracketLabel.setAttribute('data-testid', 'chord-target-bracket-label');
      bracketLabel.textContent = chordTargetLabel;
      bracket.appendChild(bracketLabel);
      bracket.style.left = Math.round(minTargetX - 14) + 'px';
      bracket.style.top = Math.round(minTargetY - 14) + 'px';
      bracket.style.width = Math.round(maxTargetX - minTargetX + 28) + 'px';
      bracket.style.height = Math.round(maxTargetY - minTargetY + 28) + 'px';
    }
    currentLightFrame = buildPadLightFrame(cells, {
      scale: scale,
      isPractice: isPracticeMode,
      view: state.view,
      targetByKey: currentTargetByKey,
      targetOrderByKey: currentGripTargetsByKey,
      pathById: pathById,
      pathIndexById: pathIndexById,
      pathMidiById: pathMidiById,
      fingerById: fingerById,
      litPracticeById: litPracticeById
    });
    var lightFrameByKey = lightFrameByCellMidi(currentLightFrame);
    for (i = 0; i < cells.length; i++) {
      var cell = cells[i];
      var lightPad = lightFrameByKey[cell.id + ':' + cell.midi];
      var inPath = !!(lightPad && lightPad.isPath);
      var displayMidi = isPracticeMode && inPath && typeof lightPad.pathMidi === 'number' ? lightPad.pathMidi : cell.midi;
      var hardwareLit = !!(lightPad && lightPad.isHardwareLit);
      var inScale = !!(lightPad && lightPad.isScale && state.view !== 'map');
      var isTonic = !!(lightPad && lightPad.isRoot);
      var isCurrent = !!(isPracticeMode && current && lightPad && lightPad.isCanonical && current.midi === cell.midi);
      var currentGripTargetIndex = lightPad ? lightPad.targetIndex : 0;
      var isCurrentGripTarget = currentGripTargetIndex > 0;
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
      if (isCurrentGripTarget) classes.push('current-grip-target');
      if (lightPad && lightPad.isTarget) classes.push('light-target');
      if (isPracticeMode && state.view === 'calibration' && isCurrent) classes.push('calibration-target');
      if (heldLevel > 0 && heldInfo.exact) classes.push('midi-held');
      if (state.rawMidiFlash && state.activeMidiCellIds[cell.id]) classes.push('midi-hit');
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
      if (lightPad) {
        key.setAttribute('data-light-role', lightPad.role);
        key.setAttribute('data-interval', String(lightPad.interval));
        key.style.setProperty('--pad-hue', String(lightPad.hue) + 'deg');
      }
      if (lightPad && typeof lightPad.pathIndex === 'number') key.setAttribute('data-path-index', String(lightPad.pathIndex));
      if (rootCell) {
        key.setAttribute('data-chain-offset', String(chainOffset(cell, rootCell)));
        key.setAttribute('data-chain-lane', hardwareLit ? String(litPracticeById[cell.id]) : chainLane(cell, rootCell));
      }
      key.setAttribute('aria-label', cell.label + octave(displayMidi) + (isCurrentGripTarget ? ', chord target ' + currentGripTargetIndex + ' of ' + currentGripCells.length + ', play together with ' + currentGripTargetNotes.join(', ') : ''));
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
      if (isTonic) key.insertAdjacentHTML('beforeend', '<span class="root-marker" aria-hidden="true">R</span>');
      if (isPracticeMode && isCurrentGripTarget && state.view === 'practice') {
        var chordFinger = document.createElement('span');
        chordFinger.className = 'finger chord-finger';
        chordFinger.textContent = String(currentGripFingerByCell[cell.id] || currentGripTargetIndex);
        chordFinger.setAttribute('aria-label', 'Chord finger ' + String(currentGripFingerByCell[cell.id] || currentGripTargetIndex));
        key.appendChild(chordFinger);
      } else if (isPracticeMode && inPath && state.view === 'practice' && !(currentEvent && currentEvent.type === 'grip')) {
        var degree = document.createElement('span');
        degree.className = 'degree-badge';
        degree.textContent = String((lightPad.pathIndex || 0) + 1);
        degree.setAttribute('aria-label', 'Step ' + String((lightPad.pathIndex || 0) + 1));
        key.appendChild(degree);
        var finger = document.createElement('span');
        finger.className = 'finger sequence-finger';
        finger.textContent = fingerShortName(lightPad.finger);
        finger.setAttribute('aria-label', 'Sequence finger ' + fingerDisplayName(lightPad.finger));
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
    els.stepReadout.textContent = currentExerciseEvents.length ? String(state.step + 1) + ' / ' + currentExerciseEvents.length : '0 / 0';
    els.currentNote.textContent = isPracticeMode && currentEvent && currentEvent.type === 'grip' ? currentEvent.targets.map(function(target) { return noteLabelFromMidi(target.midi); }).join(' + ') : (isPracticeMode && current ? noteName(current.midi) + octave(current.midi) : 'Free');
    els.currentDegree.textContent = isPracticeMode && currentEvent && currentEvent.musicalIntent && currentEvent.musicalIntent.progressionId
      ? 'Progression ' + currentEvent.musicalIntent.degree
      : (isPracticeMode && currentEvent && currentEvent.type === 'grip' ? 'Simultaneous ' + (currentEvent.musicalIntent.quality || 'multi-note') + ' grip' : (isPracticeMode && current ? 'Scale degree ' + getScaleDegree(current, scale) : 'No target in play mode'));
    var displayedGripAssignments = gripFingerAssignments(currentEvent);
    var concealCoachTarget = !!(currentEvent && currentEvent.musicalIntent && currentEvent.musicalIntent.concealTargets);
    var coachTarget = concealCoachTarget ? 'Listen, then answer' : (isPracticeMode && currentEvent && currentEvent.type === 'grip'
      ? currentEvent.targets.map(function(target) { return noteLabelFromMidi(target.midi); }).join(' + ')
      : (isPracticeMode && current ? noteLabelFromMidi(current.midi) : 'Free play'));
    if (els.coachNowPlaying) els.coachNowPlaying.textContent = coachTarget;
    if (els.dashboardNowPlaying) els.dashboardNowPlaying.textContent = coachTarget;
    if (els.dashboardSessionTitle) els.dashboardSessionTitle.textContent = els.title.textContent;
    if (els.dashboardSessionMeta) els.dashboardSessionMeta.textContent = (isPracticeMode ? 'Practice' : 'Play') + ' · ' + exercise.name;
    if (els.coachActionCue) els.coachActionCue.textContent = concealCoachTarget
      ? 'Hear the interval, then press the matching two-button shape together.'
      : (currentEvent && currentEvent.musicalIntent && currentEvent.musicalIntent.progressionId
        ? 'Progression ' + currentEvent.musicalIntent.degree + ': press every highlighted button together.'
        : describeCoachAction(currentEvent, current, currentFinger, displayedGripAssignments));
    if (els.coachNextAction) {
      var lastAttemptAccepted = state.feedbackKind === 'good';
      els.coachNextAction.textContent = lastAttemptAccepted ? 'Continue' : (isPracticeMode ? 'Hear target' : 'Play target');
      els.coachNextAction.setAttribute('aria-label', lastAttemptAccepted ? 'Continue to the next target' : 'Hear the current target');
    }
    if (els.exerciseFamily) els.exerciseFamily.value = state.exerciseFamily;
    if (els.practiceTitle) els.practiceTitle.textContent = repertoirePractice ? 'Repertoire lab' : (progressionPractice ? 'Progression lab' : 'Scale map');
    if (els.exerciseLegend) els.exerciseLegend.textContent = repertoirePractice ? 'Song' : (progressionPractice ? 'Progression' : 'Exercise');
    if (els.practiceWorkflowControls) {
      els.practiceWorkflowControls.classList.toggle('progression-layout', progressionPractice);
      els.practiceWorkflowControls.classList.toggle('repertoire-layout', repertoirePractice);
    }
    renderProgressionVoicingControls(currentExerciseEvents, chordPractice);
    renderRepertoireSectionControls(repertoirePractice);
    if (els.progressionGenreControl) els.progressionGenreControl.hidden = state.exerciseFamily !== 'progressions';
    if (els.octaveControl) els.octaveControl.hidden = chordPractice;
    if (els.rootControl) els.rootControl.hidden = chordPractice;
    if (els.fingeringControl) els.fingeringControl.hidden = chordPractice;
    if (els.progressionGenre) els.progressionGenre.value = state.progressionGenre;
    if (els.targetFinger) els.targetFinger.textContent = isPracticeMode && currentEvent && currentEvent.type === 'grip' ? 'Chord ' + displayedGripAssignments.map(function(assignment) { return String(assignment.finger); }).join(' / ') : (isPracticeMode && current ? 'Sequence ' + fingerDisplayName(currentFinger) : 'Finger --');
    if (els.targetStep) els.targetStep.textContent = isPracticeMode && currentEvent ? 'Step ' + String(state.step + 1) + ' of ' + String(currentExerciseEvents.length) : 'Step --';
    if (els.dashboardTargetMeta) els.dashboardTargetMeta.textContent = els.currentDegree.textContent + ' · ' + els.targetFinger.textContent;
    if (els.buttonReason) els.buttonReason.textContent = isPracticeMode && current ? describeButtonChoice(cells, current, rootCell) : 'Free-play chooses any physical button.';
    if (els.fingerReason) els.fingerReason.textContent = isPracticeMode && currentEvent && currentEvent.type === 'grip'
      ? 'Chord positions ' + displayedGripAssignments.map(function(assignment) { return String(assignment.finger); }).join(', ') + ' identify slots in the current simultaneous shape, not single-note sequence fingers.'
      : (isPracticeMode && current ? describeFingerChoice(strategy, currentStepIndex, currentFinger, fingers) : 'No fingering scaffold in play mode.');
    if (els.motionReason) els.motionReason.textContent = isPracticeMode && current ? describeMotionChoice(strategy, currentStepIndex, fingers) : 'Move freely in play mode.';
    if (els.ergonomicReason) {
      els.ergonomicReason.textContent = isPracticeMode && current ? ergonomicStep.text : 'Movement load: not scored in play mode.';
      els.ergonomicReason.setAttribute('data-load-level', isPracticeMode && current ? ergonomicStep.level : 'off');
    }
    if (els.gripFingeringControl && els.gripFingering) {
      var gripActive = !!(isPracticeMode && currentEvent && currentEvent.type === 'grip');
      els.gripFingeringControl.hidden = !gripActive;
      if (gripActive) {
        clearChildren(els.gripFingering);
        var primaryOption = document.createElement('option');
        primaryOption.value = 'primary';
        primaryOption.textContent = 'Pattern default';
        els.gripFingering.appendChild(primaryOption);
        currentEvent.fingering.alternatives.forEach(function(option) {
          var alternativeOption = document.createElement('option');
          alternativeOption.value = option.id;
          alternativeOption.textContent = option.label;
          els.gripFingering.appendChild(alternativeOption);
        });
        if (!currentEvent.fingering.alternatives.some(function(option) { return option.id === state.gripFingeringOption; })) state.gripFingeringOption = 'primary';
        els.gripFingering.value = state.gripFingeringOption;
      }
    }
    if (els.harmonyTriadControl) {
      var harmonyActive = !!(isPracticeMode && (state.exerciseId === 'harmony_triad' || state.exerciseId === 'voice_leading'));
      els.harmonyTriadControl.hidden = !harmonyActive;
      if (harmonyActive) {
        els.harmonyQuality.value = state.harmonyQuality;
        els.harmonyInversion.value = String(state.harmonyInversion);
      }
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
    els.midiActivity.textContent = state.midiActivity + '\n' + heldMidiActivitySummary();
    els.coachFeedback.className = 'feedback-' + state.feedbackKind;
    els.coachFeedback.textContent = state.feedback;
    els.drillScore.textContent = isPracticeMode
      ? 'Step ' + String(state.step + 1) + ' / ' + String(currentExerciseEvents.length) + ' | Score: ' + state.correctCount + ' correct / ' + state.missCount + ' missed / streak ' + state.streak
      : 'Play mode: score paused / all keys available';
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
    if (els.rgbPadTestExquis) {
      els.rgbPadTestExquis.disabled = !midiAccess || !state.exquisSysexAvailable || !midiOutput;
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
    if (els.enableMidiGate) {
      els.enableMidiGate.addEventListener('click', function() {
        enableMidi();
        state.launchGateOpen = false;
        render();
      });
    }
    if (els.continueWithoutMidi) {
      els.continueWithoutMidi.addEventListener('click', function() {
        state.launchGateOpen = false;
        render();
      });
    }
    if (els.coachToggle) {
      els.coachToggle.addEventListener('click', function() {
        state.coachOpen = !state.coachOpen;
        render();
      });
    }
    if (els.studioTabs) {
      els.studioTabs.addEventListener('click', function(event) {
        var button = event.target.closest('button[data-studio-tab]');
        if (!button) return;
        state.studioTab = button.dataset.studioTab;
        render();
      });
    }
    if (els.soundTabs) {
      els.soundTabs.addEventListener('click', function(event) {
        var button = event.target.closest('button[data-sound-tab]');
        if (!button) return;
        state.soundTab = button.dataset.soundTab;
        render();
      });
    }
    if (els.workspaceNav) {
      els.workspaceNav.addEventListener('click', function(event) {
        var button = event.target.closest('button[data-workspace]');
        if (!button) return;
        setWorkspace(button.dataset.workspace);
      });
    }
    if (els.startLibrarySession) {
      els.startLibrarySession.addEventListener('click', function() {
        setWorkspace('practice');
      });
    }
    els.tonic.addEventListener('change', function() {
      state.tonicPc = parseInt(els.tonic.value, 10) || 0;
      state.rootCellId = '';
      state.step = 0;
      render();
      syncExquisKeyModeFromUiChange();
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
      syncExquisKeyModeFromUiChange();
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
        applyCanonicalProgressionScale();
        state.step = 0;
        render();
        if (state.exquisSyncEnabled) syncExquisKeyModeToHardware();
      });
    }
    els.exercise.addEventListener('change', function() {
      state.exerciseId = els.exercise.value;
      state.exerciseFamily = exerciseFamilyForId(state.exerciseId);
      applyCanonicalProgressionScale();
      state.step = 0;
      render();
      if (state.exquisSyncEnabled) syncExquisKeyModeToHardware();
    });
    if (els.exerciseFamily) {
      els.exerciseFamily.addEventListener('change', function() {
        state.exerciseFamily = els.exerciseFamily.value;
        state.repertoireSectionId = '';
        if (state.exerciseFamily === 'progressions') {
          state.progressionGenre = 'starter';
          state.exerciseId = 'major_i_iv_vi_v';
          applyCanonicalProgressionScale();
        }
        state.step = 0;
        renderExerciseOptions();
        render();
        if (state.exquisSyncEnabled) syncExquisKeyModeToHardware();
      });
    }
    if (els.progressionGenre) {
      els.progressionGenre.addEventListener('change', function() {
        state.progressionGenre = els.progressionGenre.value;
        state.exerciseFamily = 'progressions';
        state.step = 0;
        renderExerciseOptions();
        render();
        if (state.exquisSyncEnabled) syncExquisKeyModeToHardware();
      });
    }
    if (els.repertoireSection) {
      els.repertoireSection.addEventListener('change', function() {
        state.repertoireSectionId = els.repertoireSection.value;
        state.step = 0;
        setFeedback('Song section: ' + els.repertoireSection.options[els.repertoireSection.selectedIndex].text + '.', 'neutral');
        render();
      });
    }
    if (els.repertoireTempo) {
      els.repertoireTempo.addEventListener('change', function() {
        state.repertoireTempo = parseInt(els.repertoireTempo.value, 10) || 0;
        render();
      });
    }
    if (els.repertoireCountIn) els.repertoireCountIn.addEventListener('click', playRepertoireCountIn);
    if (els.progressionGlobalNoteCount) {
      els.progressionGlobalNoteCount.addEventListener('change', function() {
        state.progressionVoicing.noteCount = parseInt(els.progressionGlobalNoteCount.value, 10) || 3;
        state.progressionVoicing.inversion = Math.min(state.progressionVoicing.noteCount - 1, state.progressionVoicing.inversion);
        state.progressionVoicing.overrides = {};
        state.step = 0;
        render();
      });
      els.progressionGlobalInversion.addEventListener('change', function() {
        state.progressionVoicing.inversion = parseInt(els.progressionGlobalInversion.value, 10) || 0;
        state.progressionVoicing.overrides = {};
        state.step = 0;
        render();
      });
      els.progressionChordRows.addEventListener('change', function(event) {
        var row = event.target.closest('[data-testid="progression-chord-row"]');
        if (!row) return;
        var step = parseInt(row.dataset.step, 10);
        var noteCount = parseInt(row.querySelector('[data-testid="progression-chord-note-count"]').value, 10) || state.progressionVoicing.noteCount;
        var inversion = parseInt(row.querySelector('[data-testid="progression-chord-inversion"]').value, 10) || 0;
        state.progressionVoicing.overrides[step] = { noteCount: noteCount, inversion: Math.min(noteCount - 1, inversion) };
        state.step = 0;
        render();
      });
    }
    els.strategy.addEventListener('change', function() {
      state.strategyId = els.strategy.value;
      render();
    });
    if (els.gripFingering) {
      els.gripFingering.addEventListener('change', function() {
        state.gripFingeringOption = els.gripFingering.value || 'primary';
        render();
      });
    }
    if (els.harmonyQuality) {
      els.harmonyQuality.addEventListener('change', function() {
        state.harmonyQuality = els.harmonyQuality.value;
        state.step = 0;
        render();
      });
    }
    if (els.harmonyInversion) {
      els.harmonyInversion.addEventListener('change', function() {
        state.harmonyInversion = parseInt(els.harmonyInversion.value, 10) || 0;
        state.step = 0;
        render();
      });
    }
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
      syncExquisPracticePadFrame();
    });
    els.prev.addEventListener('click', function() {
      state.step -= 1;
      render();
      syncExquisPracticePadFrame();
    });
    els.playStep.addEventListener('click', playCurrent);
    if (els.dashboardHearTarget) els.dashboardHearTarget.addEventListener('click', playCurrent);
    if (els.dashboardOpenSetup) els.dashboardOpenSetup.addEventListener('click', function() {
      setWorkspace('setup');
    });
    els.coachNextAction.addEventListener('click', function() {
      if (state.feedbackKind === 'good' && state.mode === 'practice') {
        state.step += 1;
        setFeedback('Practice mode: follow the current target.', 'neutral');
        render();
      } else {
        playCurrent();
      }
    });
    els.testAudio.addEventListener('click', playTestTone);
    els.playScale.addEventListener('click', playPath);
    els.enableMidi.addEventListener('click', enableMidi);
    els.syncExquis.addEventListener('click', toggleExquisSync);
    els.probeExquis.addEventListener('click', probeExquisHardware);
    els.nativeProbeExquis.addEventListener('click', probeExquisNativeWrites);
    els.rgbPadTestExquis.addEventListener('click', probeExquisRgbPad);
    els.dialListen.addEventListener('click', toggleExquisDialListen);
    els.hardwareDiagnostics.addEventListener('click', expandConsole);
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

  function rememberWorkspaceHome(name, element) {
    if (!element || workspaceHomes[name]) return;
    var anchor = document.createComment('workspace-' + name + '-home');
    element.parentNode.insertBefore(anchor, element);
    workspaceHomes[name] = anchor;
  }

  function restoreWorkspaceControl(name, element) {
    var anchor = workspaceHomes[name];
    if (!anchor || !anchor.parentNode || !element) return;
    anchor.parentNode.insertBefore(element, anchor.nextSibling);
  }

  function placeWorkspaceControls() {
    if (!els.libraryControlsSlot || !els.studioControlsSlot || !els.setupControlsSlot) return;
    if (state.workspace === 'setup') {
      els.setupControlsSlot.appendChild(els.sessionSetup);
    } else {
      restoreWorkspaceControl('sessionSetup', els.sessionSetup);
    }
    if (state.workspace === 'library') {
      els.libraryControlsSlot.appendChild(els.practiceWorkflowControls);
      if (els.progressionVoicingPanel) els.libraryControlsSlot.appendChild(els.progressionVoicingPanel);
      if (els.repertoireSectionPanel) els.libraryControlsSlot.appendChild(els.repertoireSectionPanel);
    } else {
      restoreWorkspaceControl('workflow', els.practiceWorkflowControls);
      restoreWorkspaceControl('progressionVoicing', els.progressionVoicingPanel);
      restoreWorkspaceControl('repertoireSection', els.repertoireSectionPanel);
    }
    if (state.workspace === 'studio') {
      if (els.hardwareTools) {
        els.hardwareTools.open = true;
        els.studioControlsSlot.appendChild(els.hardwareTools);
      }
      if (els.practiceTools) {
        els.practiceTools.open = true;
        els.studioControlsSlot.appendChild(els.practiceTools);
      }
    } else {
      restoreWorkspaceControl('hardwareTools', els.hardwareTools);
      restoreWorkspaceControl('practiceTools', els.practiceTools);
      restoreWorkspaceControl('consolePanel', els.consolePanel);
    }
  }

  function setWorkspace(workspace) {
    state.workspace = workspace;
    placeWorkspaceControls();
    render();
    if (advancedPracticeStep) syncExquisPracticePadFrame();
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
      exerciseLegend: document.getElementById('exerciseControlLegend'),
      exerciseButtons: document.getElementById('exerciseButtons'),
      exerciseFamily: document.getElementById('exerciseFamilySelect'),
      progressionGenre: document.getElementById('progressionGenreSelect'),
      progressionGenreControl: document.getElementById('progressionGenreControl'),
      practiceWorkflowControls: document.getElementById('practiceWorkflowControls'),
      workspaceNav: document.querySelector('[data-testid="workspace-nav"]'),
      studioTabs: document.querySelector('[data-testid="studio-tabs"]'),
      soundTabs: document.querySelector('[data-testid="sound-tabs"]'),
      studioTitle: document.getElementById('studioTitle'),
      studioDescription: document.getElementById('studioDescription'),
      connectionGate: document.getElementById('connectionGate'),
      enableMidiGate: document.getElementById('enableMidiGate'),
      continueWithoutMidi: document.getElementById('continueWithoutMidi'),
      coachToggle: document.getElementById('coachToggle'),
      sidePanel: document.querySelector('.side-panel'),
      libraryWorkspace: document.querySelector('[data-testid="library-workspace"]'),
      studioWorkspace: document.querySelector('[data-testid="studio-workspace"]'),
      setupWorkspace: document.querySelector('[data-testid="setup-workspace"]'),
      libraryControlsSlot: document.getElementById('libraryControlsSlot'),
      studioControlsSlot: document.getElementById('studioControlsSlot'),
      setupControlsSlot: document.getElementById('setupControlsSlot'),
      sessionSetup: document.querySelector('[data-testid="session-setup"]'),
      startLibrarySession: document.getElementById('startLibrarySession'),
      practiceTools: document.querySelector('[data-testid="practice-tools"]'),
      hardwareTools: document.querySelector('[data-testid="hardware-tools"]'),
      midiCoachSection: document.querySelector('[data-testid="midi-coach-section"]'),
      progressionVoicingPanel: document.getElementById('progressionVoicingPanel'),
      progressionGlobalNoteCount: document.getElementById('progressionGlobalNoteCount'),
      progressionGlobalInversion: document.getElementById('progressionGlobalInversion'),
      progressionChordRows: document.getElementById('progressionChordRows'),
      repertoireSectionPanel: document.getElementById('repertoireSectionPanel'),
      repertoireSection: document.getElementById('repertoireSectionSelect'),
      repertoireSectionSummary: document.getElementById('repertoireSectionSummary'),
      repertoireTempo: document.getElementById('repertoireTempo'),
      repertoireCountIn: document.getElementById('repertoireCountIn'),
      practiceTitle: document.getElementById('practiceTitle'),
      octaveControl: document.getElementById('octaveControl'),
      rootControl: document.getElementById('rootControl'),
      strategy: document.getElementById('strategySelect'),
      fingeringControl: document.getElementById('fingeringControl'),
      gripFingering: document.getElementById('gripFingeringSelect'),
      gripFingeringControl: document.getElementById('gripFingeringControl'),
      harmonyQuality: document.getElementById('harmonyQualitySelect'),
      harmonyInversion: document.getElementById('harmonyInversionSelect'),
      harmonyTriadControl: document.getElementById('harmonyTriadControl'),
      view: document.getElementById('viewSelect'),
      orientation: document.getElementById('orientationSelect'),
      rotateSurface: document.getElementById('rotateSurface'),
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
      dashboardNowPlaying: document.getElementById('dashboardNowPlaying'),
      dashboardTargetMeta: document.getElementById('dashboardTargetMeta'),
      dashboardSessionTitle: document.getElementById('dashboardSessionTitle'),
      dashboardSessionMeta: document.getElementById('dashboardSessionMeta'),
      dashboardHearTarget: document.getElementById('dashboardHearTarget'),
      dashboardOpenSetup: document.getElementById('dashboardOpenSetup'),
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
      coachNowPlaying: document.getElementById('coachNowPlaying'),
      coachActionCue: document.getElementById('coachActionCue'),
      coachNextAction: document.getElementById('coachNextAction'),
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
      rgbPadTestExquis: document.getElementById('rgbPadTestExquis'),
      dialListen: document.getElementById('dialListen'),
      hardwareDiagnostics: document.getElementById('hardwareDiagnostics'),
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
    rememberWorkspaceHome('sessionSetup', els.sessionSetup);
    rememberWorkspaceHome('consolePanel', els.consolePanel);
    rememberWorkspaceHome('workflow', els.practiceWorkflowControls);
    rememberWorkspaceHome('progressionVoicing', els.progressionVoicingPanel);
    rememberWorkspaceHome('repertoireSection', els.repertoireSectionPanel);
    rememberWorkspaceHome('hardwareTools', els.hardwareTools);
    rememberWorkspaceHome('practiceTools', els.practiceTools);
    placeWorkspaceControls();
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
    window.requestAnimationFrame(function() {
      render();
    });
    drawAudioScope();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
