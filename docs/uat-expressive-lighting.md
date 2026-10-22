# Expressive Light Language UAT

Expected build: `Build 1949`.

## UI Color Wheel

1. Open the landing screen and select **Enable MIDI** or **Continue without MIDI**.
2. On the **Practice** workspace, use the top **Tonic** field to select `C` and the adjacent **Scale** field to select `Major`.
3. Inspect the central Exquis play surface. Every root pad is green. The seven C-major degrees must be visibly distinct and evenly distributed around the hue wheel: `C` green, then teal, blue, violet, magenta, red-orange, and yellow-green. The next `C` returns to green.
4. Change the top **Tonic** field from `C` to `F`. Inspect the same physical C pads on the central play surface. The C-pad color changes because the interval above the selected root changed; every F root pad remains green.
5. Change the top **Scale** field from `Major` to `Minor`. Confirm the visible colored pads match the selected key and no extra prior-scale pad remains brightly lit.

## Next-Note Guidance

1. In **Exercises**, select `Technique`; select `Root to octave` in the **Exercise** control.
2. Inspect the current target pad on the central play surface. The target pad retains its interval color, has the visible `TARGET` marker, and uses a slow expanding glow.
3. Use the right-side **Practice Coach** panel's step control to advance once. Confirm the former target no longer pulses and exactly the newly selected target pad pulses.
4. Press the current target through the Exquis or on-screen pad. Confirm the central play surface advances the pulse to the next target without leaving a stale target pulse.

## Chord Guidance

1. In the left-side **Practice family** control, select `Progressions`; select `Starter`; then select `Pop I-IV-vi-V`.
2. Inspect the central play surface. Every pad in the active chord has a synchronized breathing glow and keeps its individual interval color.
3. Confirm the active chord pads retain the violet hex outlines, finger labels, and the cyan `Chord target: press together` bracket.
4. Play an incomplete or wrong chord. Confirm the central play surface keeps the same pulsing chord targets.
5. Play the complete chord. Confirm the central play surface removes the prior chord pulses and moves the synchronized pulses to the next chord.

## Physical Exquis Sync

1. In the **Studio** workspace, select **Hardware**, then press **Sync Key/Mode**.
2. Return to the **Practice** workspace and select `C Major`, then `F Major`, then `C Minor` with a two-second pause after each selection.
3. Confirm the physical Exquis pad layout matches the selected root and scale on the central play surface, with no unrelated extra pads lit.
4. Leave the device untouched for 60 seconds. Confirm the Exquis pads do not turn black, revert, or adopt an earlier key/scale layout.
5. In **Exercises**, select `Technique` and `Root to octave`. Confirm only the current target pad pulses on the physical Exquis while retaining its note color.
6. Press **Next** once. Confirm the former physical target stops pulsing and only the newly selected target pulses.
7. In **Exercises**, select **Progressions → Starter → Pop I-IV-vi-V**. Confirm every pad in the current chord pulses on the physical Exquis while retaining its individual note color.
8. Disconnect and reconnect the Exquis, then use **Reconnect Exquis** in Studio **Hardware**. Confirm the physical pad layout restores to the current UI root and scale.

## Studio Diagnostics

1. Open **Studio** and select **Hardware**. Confirm **Connection** shows **Reconnect Exquis**, the MIDI-input selector, and the current device status without opening an advanced section.
2. Press **Open diagnostics**. Confirm a readable **Console** drawer appears to the right of the hardware controls; it must not cover those controls or the main play surface.
3. Confirm every drawer action is fully readable: **Audio snapshot**, **Clear log**, **Copy**, and **Collapse**.
4. Press **Audio snapshot** and confirm new audio status text appears in the console. Press **Clear log**, accept the confirmation, and confirm the log reads `Ready.`.
5. Open **Advanced hardware research**. Confirm its warning explicitly says the actions send experimental or disruptive MIDI messages, and its buttons are named **Protocol Discovery Probe**, **Native LED Probe**, **Official Pad Color Test (Magenta)**, and **Dial Listen**.
6. Press **Official Pad Color Test (Magenta)** once. Confirm only the bottom-left pad turns magenta; all other pads, the active key/mode layout, and Settings/Sound/transport LEDs remain unchanged.
6. Press **Collapse**. Confirm the console closes cleanly and the Hardware controls remain usable.

## Failure Capture

For any failure, record the build number from the thin top build label, the Exquis firmware version, the selected Tonic/Scale/Exercise, a photo of both the central play surface and physical device, and the Studio **Console** text.
