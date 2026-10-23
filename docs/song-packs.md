# External song packs

Song packs are separate data files, loaded locally by the Songs family's
**Load song pack** control. They are not uploaded anywhere by the exhibit.

## Format

```json
{
  "format": "ssli-song-pack/v1",
  "songs": [
    {
      "title": "My authorized melody",
      "artist": "Composer, performer, or traditional source",
      "attribution": "Source, license, and/or your own authorship record",
      "soundPresetId": "subtractive::Warm Pad",
      "fxPresetId": "clean-shimmer",
      "keyTonicPc": 0,
      "keyScaleId": "ionian",
      "rootMidi": 48,
      "tempoBpm": 112,
      "durationsBeats": [0.5, 0.5, 1, 0.5, 1, 1],
      "melody": [0, 2, 4, 7, 4, 2, 0, 0],
      "scoreEventMap": [0, 1, 2, 3, 4, 5, 6, 7],
      "scoreMusicXml": "<?xml version=\"1.0\"?><score-partwise version=\"3.1\">...</score-partwise>"
    }
  ]
}
```

`artist` is the creator/source label shown next to the title in the Songs UI.
For compatibility, `attribution` is used as the label when `artist` is absent.

`soundPresetId` and `fxPresetId` are optional defaults. When present and valid,
they are applied when that song is selected, then displayed in the Practice
header as **Timbre** and **FX**. The IDs must match the current SSLI preset and
FX libraries; invalid IDs are ignored.

`keyTonicPc` (0=C through 11=B), `keyScaleId` (an SSLI scale/mode ID such as
`ionian` or `aeolian`), and `rootMidi` are an optional authored musical profile.
When present, selecting the song sets the key, scale/mode, and exact physical
Exquis root before the sequence is constructed. The physical `rootMidi` may be
different from the key tonic when the authored Exquis arrangement is transposed;
the fields deliberately preserve those two distinct musical facts.

`tempoBpm` and `durationsBeats` drive the **Audition melody** button. Each
duration is in beats at that song's tempo; omitted or invalid entries default
to an eighth note at 112 BPM. This makes phrase playback intentionally paced
rather than a fixed-rate diagnostic preview.

`melody` is a sequence of semitone offsets from the selected root (0–24). The
loader rejects malformed packs and never fetches or transmits their contents.

## Complete scores and MIDI

`scoreMusicXml` is optional, but it is the required source for a complete,
properly engraved score. It must contain a complete MusicXML `score-partwise`
or `score-timewise` document. The app renders it locally with the pinned
OpenSheetMusicDisplay SVG engraver; this gives the score conventional clefs,
key/time signatures, rests, durations, accidentals, beams, multiple voices and
multiple staves. It does **not** try to reconstruct notation with application
code.

MIDI encodes performance events, not visual engraving. Convert an authorized
MIDI file to MusicXML with MuseScore Studio before adding it to a pack, then
put that MusicXML in `scoreMusicXml`. MuseScore officially supports MIDI import
and MusicXML export, including batch conversion from its command-line mode.
For a local conversion, run:

```powershell
& "C:\Users\hanis\AppData\Roaming\clairvoyance\repos\super-synth-lab-exquis-exhibit\tools\convert-midi-to-musicxml.ps1" `
  -InputMidi "C:\absolute\path\to\authorized-source.mid" `
  -OutputMusicXml "C:\absolute\path\to\score.musicxml" `
  -MuseScoreExe "C:\Program Files\MuseScore 4\bin\MuseScore4.exe"
```

Keep `melody` in the exact same score order as the Exquis part being drilled:
it drives interactive practice and audition timing, while `scoreMusicXml`
remains the authoritative complete score shown to the player.

The first MusicXML part is the playable part. `scoreEventMap` is optional when
every engraved note in that part is playable; otherwise map each engraved note
position to its zero-based `melody` index and use `null` for rests or notation
that is visible but not part of the Exquis drill. This keeps a score with rests,
cue notes, or accompaniment interactive without guessing from rendered SVG.

For longer scores, the default display follows the current and next engraved
measure. **Full score** expands back to the entire score; **Follow measures**
returns to the two-measure learning view.

Distribute each pack with its own rights record. A pack author is responsible
for the authorization to share its melody data and title in the intended
territories. Use `song-packs/example-authorized-song-pack.ssli-songpack.json`
as the starting template.
