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
      "attribution": "Source, license, and/or your own authorship record",
      "melody": [0, 2, 4, 7, 4, 2, 0, 0]
    }
  ]
}
```

`melody` is a sequence of semitone offsets from the selected root (0–24). The
loader rejects malformed packs and never fetches or transmits their contents.

Distribute each pack with its own rights record. A pack author is responsible
for the authorization to share its melody data and title in the intended
territories. Use `song-packs/example-authorized-song-pack.ssli-songpack.json`
as the starting template.
