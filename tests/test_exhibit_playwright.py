import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


try:
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover - makes static test runs possible without Playwright installed
    sync_playwright = None


class PlaywrightExhibitTests(unittest.TestCase):
    STATED_FAILURE_REGRESSIONS = {
        "default_rotation_button_must_read_rotate_180": "test_regression_default_rotation_button_reads_rotate_180",
        "default_exquis_layout_must_be_horizontal_corrected_180": "test_regression_default_exquis_layout_is_horizontal_corrected_180",
        "default_horizontal_must_not_be_off_by_180": "test_regression_default_horizontal_is_not_off_by_180",
        "no_scroll_must_not_clip_window": "test_regression_no_scroll_layout_does_not_clip_right_rail",
        "hex_ui_must_not_look_like_cartesian_grid": "test_regression_keyboard_surface_has_no_cartesian_background_grid",
        "hex_ui_must_not_float_off_center": "test_regression_hex_field_is_centered_in_keyboard_viewport",
        "hex_spacing_must_match_compact_honeycomb": "test_regression_exquis_key_spacing_matches_compact_physical_honeycomb",
        "hex_field_must_match_tall_exquis_silhouette": "test_regression_hex_field_matches_tall_exquis_silhouette",
        "vertical_layout_must_be_tightly_packed": "test_regression_vertical_layout_is_tightly_packed",
        "hex_neighbors_must_touch_without_gaps_or_overlap": "test_regression_hex_neighbors_touch_without_gaps_or_overlap",
        "supported_rotations_must_preserve_hex_layout": "test_regression_supported_rotations_preserve_hex_layout",
        "unsupported_rotation_buttons_must_not_be_exposed": "test_regression_unsupported_rotation_buttons_are_not_exposed",
        "practice_must_light_only_two_exquis_chains": "test_regression_practice_lights_only_two_exquis_chains",
        "hardware_lit_keys_must_all_be_in_selected_key": "test_regression_hardware_lit_keys_are_all_in_selected_key",
        "default_c_major_leds_must_match_exquis_product_photo": "test_regression_default_c_major_leds_match_product_photo",
        "fingering_must_only_label_two_lit_chains": "test_regression_fingering_labels_only_two_lit_chains",
        "keyboard_zoom_must_not_show_giant_empty_tray": "test_regression_keyboard_viewport_is_tight_around_physical_surface",
        "no_scroll_must_keep_primary_controls_visible": "test_regression_laptop_no_scroll_keeps_primary_controls_visible",
        "midi_status_regions_must_remain_visible_on_laptop": "test_regression_midi_status_regions_remain_visible_and_live_on_laptop",
        "fingering_root_must_not_be_overwritten": "test_regression_selected_root_keeps_first_fingering_assignment",
        "fingering_labels_must_stay_valid": "test_regression_fingering_labels_are_valid_for_visible_path",
        "wrist_led_pairs_must_allow_same_finger_for_nearby_steps": "test_regression_wrist_led_pairs_allow_same_finger_for_d3_e3",
        "natural_clusters_must_prioritize_human_finger_names": "test_regression_natural_clusters_prioritize_human_finger_names",
        "natural_clusters_must_be_default_fingering_strategy": "test_regression_natural_clusters_is_default_fingering_strategy",
        "scale_fingering_must_ascend_root_to_octave": "test_regression_scale_path_ascends_root_to_octave",
        "practice_octaves_must_match_physical_play_labels": "test_regression_practice_octaves_match_physical_play_labels",
        "duplicate_pitch_choices_must_prefer_centered_chain_cell": "test_regression_duplicate_pitch_choices_prefer_centered_chain_cell",
        "two_octave_exercise_must_use_physical_two_octave_path": "test_regression_two_octave_exercise_uses_physical_two_octave_path",
        "practice_console_must_not_cover_two_octave_keys": "test_regression_console_does_not_cover_two_octave_practice_keys",
        "exercise_selector_must_change_actual_practice_path": "test_regression_exercise_selector_changes_actual_practice_path",
        "inner_chain_exercise_must_descend_same_path": "test_regression_inner_chain_ladder_descends_same_two_chain_path",
        "root_return_exercise_must_recenter_between_scale_tones": "test_regression_root_return_exercise_recenters_between_scale_tones",
        "practice_mode_must_show_actionable_targets": "test_regression_practice_mode_shows_actionable_targets",
        "practice_mode_must_explain_button_finger_motion_choices": "test_regression_practice_mode_explains_button_finger_motion_choices",
        "practice_mode_must_score_ergonomic_movement_load": "test_regression_practice_mode_scores_ergonomic_movement_load",
        "ergonomic_model_must_extend_to_other_keys_and_modes": "test_regression_ergonomic_model_extends_to_other_keys_and_modes",
        "ergonomic_model_must_cover_every_key_mode_octave": "test_regression_ergonomic_model_covers_every_key_mode_octave",
        "practice_mode_must_show_visible_hand_and_two_octave_controls": "test_regression_practice_mode_shows_visible_hand_and_two_octave_controls",
        "hand_side_and_octave_side_must_be_deconflated": "test_regression_hand_side_and_octave_side_are_deconflated",
        "practice_header_controls_must_not_overlap": "test_regression_practice_header_controls_do_not_overlap",
        "practice_header_controls_must_follow_information_hierarchy": "test_regression_practice_header_controls_follow_information_hierarchy",
        "two_octave_paths_must_extend_to_other_keys_and_modes": "test_regression_two_octave_paths_extend_to_other_keys_and_modes",
        "practice_path_must_mark_hand_shift_steps": "test_regression_practice_path_marks_hand_shift_steps",
        "play_mode_must_leave_full_surface_available": "test_regression_play_mode_leaves_full_surface_available",
        "play_mode_must_not_foreground_practice_settings": "test_regression_play_mode_subtitle_hides_practice_scaffold",
        "play_mode_midi_must_not_score_or_advance": "test_regression_play_mode_midi_does_not_score_or_advance",
        "practice_mode_controls_must_be_mode_contingent": "test_regression_practice_controls_are_hidden_in_play_mode",
        "two_octave_must_show_resolved_root_octave": "test_regression_two_octave_keeps_resolved_octave_state_visible",
        "practice_key_labels_must_be_explicit": "test_regression_practice_key_labels_are_explicit",
        "play_path_must_follow_visible_practice_order": "test_regression_play_path_audio_follows_visible_practice_order",
        "two_octave_play_path_must_follow_visible_order": "test_regression_two_octave_play_path_audio_follows_visible_order",
        "guide_tone_must_be_separate_from_ssli_sound_controls": "test_regression_guide_tone_is_separate_from_ssli_sound_controls",
        "exquis_ui_must_not_be_tiny": "test_regression_exquis_ui_is_visually_dominant",
        "ssli_presets_need_engine_category_preset_selectors": "test_regression_ssli_preset_selectors_are_hierarchical",
        "ssli_engine_dropdown_defaults_to_mature_engines": "test_regression_sound_engine_dropdown_defaults_to_mature_engines_with_show_all_opt_in",
        "fx_chains_need_category_preset_selectors": "test_regression_fx_chain_selectors_are_hierarchical",
        "fx_controls_must_share_one_visual_row": "test_regression_fx_controls_share_one_visual_row",
        "preset_changes_must_change_generated_sound": "test_regression_preset_changes_audio_graph_not_just_label",
        "filter_and_fx_chain_must_use_real_ssli_audio_api": "test_regression_filter_and_fx_controls_call_ssli_audio_api",
        "ssli_engines_must_initialize_before_selected_preset_playback": "test_regression_ssli_engine_initializes_before_selected_preset_playback",
        "exquis_midi_must_use_ssli_sustained_notes_and_expression": "test_regression_exquis_midi_uses_ssli_sustained_note_and_expression_api",
        "exquis_low_velocity_midi_must_still_start_audible_ssli_voice": "test_regression_exquis_low_velocity_starts_audible_ssli_voice",
        "exquis_raw_midi_must_not_be_octave_transposed": "test_regression_exquis_raw_midi_is_not_octave_transposed",
        "exquis_grid_octave_labels_must_match_c3_to_c4_practice_range": "test_regression_exquis_grid_octaves_match_c3_to_c4_practice_range",
        "exquis_octave_fix_must_not_move_every_note": "test_regression_octave_rollover_uses_chromatic_row_math",
        "exquis_soft_touch_expression_must_not_be_nearly_silent": "test_regression_exquis_soft_touch_expression_is_audible",
        "test_tone_must_use_loud_local_output": "test_regression_test_tone_uses_loud_local_output",
        "test_tone_must_bypass_ssli_for_local_scope": "test_regression_test_tone_bypasses_ssli_and_drives_local_scope",
        "test_tone_must_be_loud_diagnostic_reference": "test_regression_test_tone_uses_loud_local_output",
        "waveform_must_show_visible_signal": "test_regression_test_tone_scope_draws_visible_waveform",
        "test_tone_scope_must_use_real_audio_not_mocked_analyser": "test_regression_real_test_tone_drives_scope_without_mocked_audio_context",
        "ssli_midi_sustain_must_use_user_performance_volume": "test_regression_ssli_midi_sustain_uses_performance_volume",
        "celesta_midi_must_not_use_output_boost_compensation": "test_regression_ssli_celesta_does_not_use_output_boost_compensation",
        "rhodes_midi_must_not_use_output_boost_compensation": "test_regression_ssli_rhodes_does_not_use_output_boost_compensation",
        "ssli_midi_sustain_must_not_wrap_runtime_output": "test_regression_ssli_midi_sustain_does_not_wrap_runtime_output",
        "exquis_midi_must_use_linear_velocity_and_live_pressure_expression": "test_regression_exquis_midi_uses_linear_velocity_and_live_pressure_expression",
        "exquis_live_pressure_must_not_stack_expression_gain_into_garble": "test_regression_live_pressure_caps_expression_gain_during_repeated_play",
        "staggered_physical_plucked_chords_must_not_use_solo_boost_or_idle_cleanup": "test_regression_staggered_physical_plucked_chords_keep_chord_headroom",
        "repeated_exquis_chords_must_not_accumulate_playback_latency": "test_regression_repeated_exquis_chords_do_not_accumulate_playback_latency",
        "diagnostic_logging_must_not_block_midi_hot_path": "test_regression_diagnostic_logging_is_batched_off_hot_path",
        "fm_midi_must_translate_exquis_pressure_without_global_expression": "test_regression_fm_midi_translates_exquis_pressure_without_global_expression",
        "low_register_subtractive_poly_must_remain_audible": "test_regression_low_register_subtractive_poly_preserves_volume",
        "mpe_channel_reuse_must_release_previous_voice": "test_regression_mpe_channel_reuse_releases_previous_voice",
        "mpe_same_note_new_channel_must_release_previous_owner": "test_regression_mpe_same_note_on_new_channel_releases_previous_ssli_owner",
        "exquis_channel_16_notes_must_play_as_mpe_notes": "test_regression_exquis_channel_16_note_events_are_playable_mpe_notes",
        "low_velocity_release_bounce_must_not_retrigger_note": "test_regression_low_velocity_release_bounce_does_not_retrigger_note",
        "low_velocity_retrigger_during_short_hold_must_not_double_start_voice": "test_regression_low_velocity_retrigger_during_short_hold_does_not_double_start_voice",
        "immediate_exquis_note_off_must_not_drop_chord_member": "test_regression_immediate_note_off_is_delayed_to_preserve_chord_member",
        "midi_voice_bursts_must_cleanup_all_ssli_sustained_voices_when_idle": "test_regression_midi_voice_bursts_cleanup_all_ssli_sustained_voices_when_idle",
        "repeated_exquis_notes_must_not_reapply_preset_or_leak_ssli_voices": "test_regression_repeated_exquis_notes_do_not_reapply_preset_or_leak_ssli_voices",
        "play_mode_chords_must_keep_independent_ssli_voice_ownership": "test_regression_play_mode_chords_keep_independent_ssli_voice_ownership",
        "plucked_presets_must_strum_simultaneous_buttons": "test_regression_plucked_presets_buffer_simultaneous_note_ons_into_strum",
        "non_plucked_presets_must_not_strum_simultaneous_buttons": "test_regression_non_plucked_presets_keep_immediate_note_ons",
        "released_buffered_notes_must_not_leak_to_synth": "test_regression_released_buffered_strum_note_does_not_start_synth_voice",
        "stale_note_off_after_prune_must_not_clear_current_touch": "test_regression_stale_note_off_after_prune_does_not_double_stop_or_clear_current_touch",
        "pressure_zero_for_one_note_must_not_collapse_other_notes": "test_regression_pressure_zero_for_one_held_note_does_not_collapse_expression_for_other_notes",
        "single_note_pressure_zero_must_not_fall_back_to_velocity": "test_regression_single_note_pressure_zero_does_not_fall_back_to_velocity",
        "pressure_flood_must_not_spam_ssli_expression": "test_regression_pressure_flood_is_coalesced_before_ssli_expression",
        "play_mode_pressure_must_affect_subtractive_audio": "test_regression_play_mode_pressure_changes_actual_subtractive_audio",
        "play_mode_pressure_must_reach_physical_runtime": "test_regression_play_mode_pressure_reaches_actual_physical_runtime",
        "same_channel_buttons_must_remain_independent": "test_regression_same_channel_buttons_keep_independent_held_voices",
        "enable_midi_must_be_first_prominent_side_rail_action": "test_regression_enable_midi_is_first_prominent_side_rail_action",
        "midi_diagnostics_console_must_be_visible": "test_regression_midi_diagnostics_console_is_visible",
        "exquis_sysex_helpers_must_encode_official_root_scale_messages": "test_regression_exquis_sysex_helpers_encode_official_root_scale_messages",
        "exquis_key_mode_sync_must_use_official_developer_sysex": "test_regression_exquis_key_mode_sync_uses_official_developer_sysex",
        "exquis_incoming_root_scale_sysex_must_update_ui": "test_regression_exquis_incoming_root_scale_sysex_updates_ui_without_echo",
        "exquis_sync_must_fallback_when_sysex_permission_denied": "test_regression_exquis_sync_falls_back_to_input_only_when_sysex_permission_denied",
        "exquis_probe_must_capture_official_and_legacy_sysex": "test_regression_exquis_probe_sends_official_and_legacy_diagnostics",
        "exquis_dials_must_drive_and_report_native_key_mode": "test_regression_exquis_dial_listen_uses_settings_encoder_developer_mode_and_logs_dials",
        "exquis_native_write_probe_must_sweep_developer_masks": "test_regression_exquis_native_probe_sweeps_official_write_masks",
        "exquis_edge_controls_must_be_labeled_in_ui": "test_regression_exquis_edge_controls_are_labeled_and_show_capture_state",
        "exquis_edge_controls_must_follow_physical_orientation": "test_regression_exquis_edge_controls_follow_orientation_layout",
        "exquis_side_controls_must_rotate_in_physical_bottom_to_top_order": "test_regression_exquis_side_controls_rotate_in_physical_bottom_to_top_order",
        "exquis_hardware_controls_must_use_physical_shapes": "test_regression_exquis_hardware_controls_use_physical_shapes",
        "horizontal_hardware_slab_must_not_waste_vertical_space": "test_regression_horizontal_hardware_slab_does_not_waste_vertical_space",
        "tablet_horizontal_hardware_must_not_clip_stage": "test_regression_tablet_horizontal_hardware_fits_stage",
        "mobile_build_badge_must_not_cover_keys": "test_regression_mobile_build_badge_does_not_cover_playable_keys",
        "horizontal_exquis_layout_must_fit_without_dead_band_or_clipped_stepper": "test_regression_horizontal_exquis_layout_fits_stage_without_dead_band_or_clipped_stepper",
        "audio_diagnostics_must_include_ssli_voice_pool_health": "test_regression_audio_diag_reports_ssli_voice_pool_health",
        "console_actions_must_fit_on_one_row": "test_regression_console_actions_fit_on_one_row",
        "midi_note_highlight_must_match_exact_midi_note_only": "test_regression_midi_highlight_matches_exact_note_only",
        "midi_duplicate_note_highlight_must_use_centered_physical_cell": "test_regression_midi_duplicate_note_highlights_centered_physical_cell",
        "midi_note_on_must_be_blue_white_not_root_white": "test_regression_midi_note_on_color_is_distinct_from_root_white",
        "all_tonic_pitch_class_keys_must_be_root_white": "test_regression_all_c_keys_are_tonic_in_default_c_major",
        "horizontal_and_vertical_scale_leds_must_stay_visibly_lit": "test_regression_scale_leds_are_visible_in_horizontal_and_vertical",
        "horizontal_layout_must_rotate_physical_key_shapes": "test_regression_horizontal_layout_rotates_physical_key_shapes",
        "hexes_must_be_regular_and_share_edges": "test_regression_hexes_are_regular_and_share_edges",
        "keyboard_must_not_remain_tiny_when_stage_has_room": "test_regression_keyboard_scales_to_available_stage_space",
        "presets_must_not_play_default_sound": "test_regression_ssli_runtime_preset_changes_played_instrument",
        "preset_sweep_must_intone_distinct_real_engine_audio": "test_regression_preset_signature_check_intones_distinct_real_engines",
        "midi_preset_sweep_must_intone_selected_engine_audio": "test_regression_preset_signature_check_intones_physical_koto_through_midi",
        "mature_engine_categories_must_pass_six_note_poly_pressure_audio_sweep": "test_regression_preset_sweep_runs_mature_engine_category_poly_pressure_audio",
        "category_smoke_must_not_skip_hard_first_presets": "test_regression_first_noise_industrial_preset_survives_six_note_poly_pressure_audio",
        "subtractive_presets_must_not_create_out_of_range_filter_cutoffs": "test_regression_subtractive_runtime_preset_filter_cutoff_is_normalized",
        "sound_selectors_must_use_live_ssli_preset_api": "test_regression_sound_selectors_use_live_ssli_preset_api_when_available",
        "physical_koto_must_apply_physical_model_settings": "test_regression_physical_koto_applies_model_settings_without_preview_expression_override",
        "physical_midi_must_use_tracked_ssli_sustained_voice": "test_regression_physical_midi_uses_tracked_ssli_sustained_voice_with_velocity",
        "physical_midi_idle_must_cleanup_engine_tails": "test_regression_physical_midi_idle_calls_physical_all_notes_off",
        "physical_midi_pressure_must_not_drive_global_expression": "test_regression_physical_midi_pressure_does_not_call_global_expression",
        "physical_concurrent_voices_must_not_force_every_note_to_max_velocity": "test_regression_physical_concurrent_voices_use_shaped_velocity_not_max_velocity",
        "simultaneous_two_note_physical_attack_must_not_over_dampen_second_note": "test_regression_two_simultaneous_physical_notes_keep_shared_attack_velocity",
        "simultaneous_adjacent_pluck_notes_must_use_general_voice_load_policy": "test_regression_adjacent_pluck_uses_general_voice_load_policy",
        "simultaneous_adjacent_pluck_notes_must_have_stable_audio_output": "test_regression_adjacent_pluck_has_stable_audio_output",
        "plucked_strum_must_use_group_headroom_from_first_note": "test_regression_plucked_strum_uses_group_headroom_from_first_note",
        "plucked_strum_must_ignore_held_pressure_and_auto_damp": "test_regression_plucked_strum_ignores_held_pressure_and_auto_damps",
        "plucked_held_one_shot_must_keep_voice_ownership_until_note_off": "test_regression_plucked_held_one_shot_keeps_voice_ownership_until_note_off",
        "plucked_strum_must_play_notes_released_after_flush": "test_regression_plucked_strum_plays_note_released_after_flush_before_slot",
        "plucked_strum_must_play_capture_matured_notes_when_timer_flush_is_late": "test_regression_plucked_strum_plays_capture_matured_note_even_when_flush_timer_is_late",
        "real_plucked_strum_must_play_notes_released_after_flush": "test_regression_real_plucked_strum_plays_note_released_after_flush_before_slot",
        "three_note_plucked_strum_must_have_stable_audio_output": "test_regression_three_note_plucked_strum_has_stable_audio_output",
        "physical_poly_aftertouch_must_remain_per_note": "test_regression_four_note_physical_voices_track_pressure_independently_without_global_expression",
        "plucked_physical_pressure_must_be_forwarded_per_note_to_audio_engine": "test_regression_plucked_physical_pressure_is_forwarded_per_note_to_audio_engine",
        "six_note_physical_pressure_must_be_audio_tested": "test_regression_six_note_physical_pressure_flow_has_stable_final_audio_output",
        "six_note_physical_voices_must_keep_independent_pressure_updates": "test_regression_six_note_physical_voices_keep_independent_pressure_updates",
        "physical_pressure_stream_must_rate_limit_per_note_without_dropping_release": "test_regression_physical_pressure_stream_is_rate_limited_per_note_but_release_passes",
        "midi_preset_cache_must_verify_live_ssli_engine": "test_regression_midi_reapplies_preset_when_live_ssli_engine_does_not_match_cache",
        "midi_ssli_fallback_must_report_missing_runtime_api": "test_regression_midi_reports_missing_ssli_runtime_api_before_local_fallback",
        "ssli_preset_selection_must_retry_when_runtime_loads_late": "test_regression_preset_selection_retries_when_ssli_runtime_loads_late",
        "fm_dx_rhodes_must_not_be_noisy_poppy_or_bell_like": "test_regression_fm_dx_rhodes_uat_audio_acceptance",
        "uat_quiet_spot_presets_must_clear_single_note_floor": "test_regression_uat_quiet_spot_presets_clear_single_note_floor",
        "physical_marimba_c3_must_not_be_blown_out_relative_to_c4": "test_regression_physical_marimba_c3_is_balanced_against_c4",
        "uat_spot_presets_must_not_require_hard_velocity_for_loudness": "test_regression_uat_spot_presets_have_medium_velocity_loudness",
        "uat_fm_spot_presets_must_not_collapse_to_same_timbre": "test_regression_uat_fm_spot_presets_do_not_collapse_to_same_timbre",
    }

    @classmethod
    def setUpClass(cls):
        if sync_playwright is None:
            raise unittest.SkipTest("Python Playwright is not installed")
        subprocess.run(["python", "build.py"], cwd=ROOT, check=True)
        cls.html_path = ROOT / "index.html"

    def setUp(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        self.page = self.browser.new_page(viewport={"width": 1280, "height": 820})
        self.page.goto(self.html_path.as_uri())

    def tearDown(self):
        self.browser.close()
        self.pw.stop()

    def open_audio_drawer(self):
        drawer = self.page.locator('[data-testid="audio-drawer"]')
        if drawer.count() == 0:
            return
        if not drawer.evaluate("el => el.open"):
            drawer.locator("summary").click()

    def test_every_stated_failure_has_named_regression_test(self):
        available = {name for name in dir(type(self)) if name.startswith("test_")}
        for failure_id, test_name in self.STATED_FAILURE_REGRESSIONS.items():
            self.assertIn(test_name, available, failure_id)

    def test_build_version_badge_is_visible_and_matches_runtime_cache_key(self):
        badge = self.page.locator('[data-testid="build-version"]')
        self.assertTrue(badge.is_visible())
        badge_box = badge.bounding_box()
        self.assertIsNotNone(badge_box)
        self.assertGreaterEqual(badge_box["width"], 120)
        self.assertGreaterEqual(badge_box["height"], 28)
        self.assertIn("Build", badge.inner_text())
        version = badge.locator("b").inner_text()
        self.assertRegex(version, r"^Build \d+$")
        runtime = self.page.evaluate("() => window.SSLI_EXQUIS_BUILD")
        self.assertEqual(runtime["version"], version)
        self.assertRegex(runtime["timestamp"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [AP]M ET$")
        self.assertRegex(runtime["timestampUtc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertIn("ssli/index.html?v=" + runtime["timestampUtc"], self.page.locator("#ssliEngineFrame").get_attribute("src"))

    def test_renders_61_keys(self):
        self.assertEqual(self.page.locator('[data-testid="exquis-key"]').count(), 61)

    def test_regression_default_rotation_button_reads_rotate_180(self):
        self.assertEqual(self.page.locator('[data-testid="orientation-select"]').input_value(), "horizontal")
        self.assertIn("Rotate 180", self.page.locator('[data-testid="rotate-surface"]').inner_text())
        self.assertEqual(self.page.locator('[data-testid="keyboard"]').get_attribute("data-rotation"), "0")

    def test_regression_default_exquis_layout_is_horizontal_corrected_180(self):
        metrics = self.page.evaluate("""() => {
          const keyboard = document.querySelector('[data-testid="keyboard"]').getBoundingClientRect();
          const keys = [...document.querySelectorAll('[data-testid="exquis-key"]')].map((el) => {
            const box = el.getBoundingClientRect();
            return { id: el.dataset.cellId, box };
          });
          const boxes = keys.map((key) => key.box);
          const field = {
            left: Math.min(...boxes.map((box) => box.left)),
            right: Math.max(...boxes.map((box) => box.right)),
            top: Math.min(...boxes.map((box) => box.top)),
            bottom: Math.max(...boxes.map((box) => box.bottom))
          };
          const byRow = {};
          keys.forEach((key) => {
            const row = Number(key.id.match(/r(\\d+)c/)[1]);
            byRow[row] = (byRow[row] || 0) + 1;
          });
          return {
            keyboardAspect: Math.max(keyboard.height, keyboard.width) / Math.min(keyboard.height, keyboard.width),
            fieldAspect: Math.max(field.bottom - field.top, field.right - field.left) / Math.min(field.bottom - field.top, field.right - field.left),
            rowCounts: Object.keys(byRow).sort((a, b) => Number(a) - Number(b)).map((row) => byRow[row]),
            fieldLeftPad: field.left - keyboard.left,
            fieldRightPad: keyboard.right - field.right
          };
        }""")
        self.assertGreater(metrics["keyboardAspect"], 1.20)
        self.assertGreater(metrics["fieldAspect"], 1.62)
        self.assertLess(metrics["fieldAspect"], 1.66)
        self.assertEqual(metrics["rowCounts"], [6, 5, 6, 5, 6, 5, 6, 5, 6, 5, 6])
        self.assertLess(abs(metrics["fieldLeftPad"] - metrics["fieldRightPad"]), 28)

    def test_regression_default_horizontal_is_not_off_by_180(self):
        positions = self.page.evaluate("""() => {
          const box = (id) => document.querySelector(`[data-cell-id="${id}"]`).getBoundingClientRect();
          return {
            r0: box('r0c0').left,
            r10: box('r10c0').left,
            rotation: document.querySelector('[data-testid="keyboard"]').dataset.rotation,
            orientation: document.querySelector('[data-testid="orientation-select"]').value
          };
        }""")
        self.assertEqual(positions["orientation"], "horizontal")
        self.assertEqual(positions["rotation"], "0")
        self.assertGreater(positions["r0"], positions["r10"])

    def test_regression_horizontal_layout_rotates_physical_key_shapes(self):
        self.assertEqual(self.page.locator('[data-testid="orientation-select"]').input_value(), "horizontal")
        rotation = self.page.locator('[data-testid="exquis-key"]').first.evaluate("""el => {
          const transform = getComputedStyle(el).transform;
          return transform;
        }""")
        label_rotation = self.page.locator('[data-testid="exquis-key"] .key-label').first.evaluate("el => getComputedStyle(el).transform")
        self.assertNotIn("matrix(1, 0, 0, 1", rotation)
        self.assertNotEqual(rotation, "none")
        self.assertNotEqual(label_rotation, "none")

    def test_regression_vertical_layout_is_tightly_packed(self):
        self.page.select_option('[data-testid="orientation-select"]', "vertical")
        metrics = self.page.evaluate("""() => {
          const box = (id) => document.querySelector(`[data-cell-id="${id}"]`).getBoundingClientRect();
          const center = (b) => ({ x: (b.left + b.right) / 2, y: (b.top + b.bottom) / 2 });
          const dist = (a, b) => Math.hypot(center(a).x - center(b).x, center(a).y - center(b).y);
          const key = document.querySelector('[data-testid="exquis-key"]').getBoundingClientRect();
          const sameRow = dist(box('r0c0'), box('r0c1'));
          const adjacentRow = dist(box('r0c0'), box('r1c0'));
          const twoRows = dist(box('r0c0'), box('r2c0'));
          return {
            keyHeight: key.height,
            sameRow,
            adjacentRow,
            twoRows,
            sameRowRatio: sameRow / key.height,
            adjacentRatio: adjacentRow / key.height,
            twoRowRatio: twoRows / key.height
          };
        }""")
        self.assertGreaterEqual(metrics["sameRowRatio"], 0.865)
        self.assertLessEqual(metrics["sameRowRatio"], 0.867)
        self.assertGreaterEqual(metrics["adjacentRatio"], 0.865)
        self.assertLessEqual(metrics["adjacentRatio"], 0.867)
        self.assertGreaterEqual(metrics["twoRowRatio"], 1.49)
        self.assertLessEqual(metrics["twoRowRatio"], 1.51)

    def test_regression_hex_neighbors_touch_without_gaps_or_overlap(self):
        def assert_honeycomb(orientation):
            self.page.select_option('[data-testid="orientation-select"]', orientation)
            metrics = self.page.evaluate("""() => {
              const box = (id) => document.querySelector(`[data-cell-id="${id}"]`).getBoundingClientRect();
              const center = (b) => ({ x: (b.left + b.right) / 2, y: (b.top + b.bottom) / 2 });
              const a = center(box('r0c0'));
              const b = center(box('r0c1'));
              const c = center(box('r1c0'));
              const d = center(box('r2c0'));
              const key = document.querySelector('[data-testid="exquis-key"]').getBoundingClientRect();
              return {
                keyW: key.width,
                keyH: key.height,
                sameDx: Math.abs(b.x - a.x),
                sameDy: Math.abs(b.y - a.y),
                adjacentDx: Math.abs(c.x - a.x),
                adjacentDy: Math.abs(c.y - a.y),
                twoRowDx: Math.abs(d.x - a.x),
                twoRowDy: Math.abs(d.y - a.y)
              };
            }""")
            values = [orientation, metrics]
            same = sorted([metrics["sameDx"], metrics["sameDy"]])
            adjacent = sorted([metrics["adjacentDx"], metrics["adjacentDy"]])
            two_row = sorted([metrics["twoRowDx"], metrics["twoRowDy"]])
            self.assertLessEqual(same[0], 1.1, values)
            if orientation == "horizontal":
                self.assertLessEqual(abs(same[1] - metrics["keyH"]), 1.1, values)
                self.assertLessEqual(abs(adjacent[0] - metrics["keyH"] / 2), 1.1, values)
                self.assertLessEqual(abs(adjacent[1] - metrics["keyW"] * 0.75), 1.1, values)
                self.assertLessEqual(two_row[0], 1.1, values)
                self.assertLessEqual(abs(two_row[1] - metrics["keyW"] * 1.5), 1.1, values)
            else:
                self.assertLessEqual(abs(same[1] - metrics["keyW"]), 1.1, values)
                self.assertLessEqual(abs(adjacent[0] - metrics["keyW"] / 2), 1.1, values)
                self.assertLessEqual(abs(adjacent[1] - metrics["keyH"] * 0.75), 1.1, values)
                self.assertLessEqual(two_row[0], 1.1, values)
                self.assertLessEqual(abs(two_row[1] - metrics["keyH"] * 1.5), 1.1, values)

        assert_honeycomb("vertical")
        assert_honeycomb("horizontal")

    def test_regression_hexes_are_regular_and_share_edges(self):
        def check(orientation):
            self.page.select_option('[data-testid="orientation-select"]', orientation)
            metrics = self.page.evaluate("""() => {
              const basePts = [[0.5,0],[1,0.25],[1,0.75],[0.5,1],[0,0.75],[0,0.25]];
              function matrix(el) {
                const transform = getComputedStyle(el).transform;
                if (transform === 'none') return [1,0,0,1,0,0];
                return transform.match(/matrix\\(([^)]+)\\)/)[1].split(',').map(Number);
              }
              function poly(id) {
                const el = document.querySelector(`[data-cell-id="${id}"]`);
                const b = el.getBoundingClientRect();
                const m = matrix(el);
                const cx = b.left + b.width / 2;
                const cy = b.top + b.height / 2;
                const w = Number(getComputedStyle(el).width.replace('px', ''));
                const h = Number(getComputedStyle(el).height.replace('px', ''));
                return basePts.map(([px, py]) => {
                  const lx = px * w - w / 2;
                  const ly = py * h - h / 2;
                  return { x: cx + m[0] * lx + m[2] * ly, y: cy + m[1] * lx + m[3] * ly };
                });
              }
              function edges(points) {
                return points.map((point, index) => [point, points[(index + 1) % points.length]]);
              }
              function length(edge) {
                return Math.hypot(edge[1].x - edge[0].x, edge[1].y - edge[0].y);
              }
              function bestSharedEdge(a, b) {
                let best = Infinity;
                for (const edgeA of edges(poly(a))) {
                  for (const edgeB of edges(poly(b))) {
                    const reversed = [edgeB[1], edgeB[0]];
                    const error = Math.hypot(edgeA[0].x - reversed[0].x, edgeA[0].y - reversed[0].y)
                      + Math.hypot(edgeA[1].x - reversed[1].x, edgeA[1].y - reversed[1].y);
                    best = Math.min(best, error);
                  }
                }
                return best;
              }
              const sideLengths = edges(poly('r0c0')).map(length);
              return {
                sideLengths,
                sideSpread: Math.max(...sideLengths) - Math.min(...sideLengths),
                sameRowEdgeError: bestSharedEdge('r0c0', 'r0c1'),
                adjacentRowEdgeError: bestSharedEdge('r0c0', 'r1c0')
              };
            }""")
            self.assertLess(metrics["sideSpread"], 0.75, [orientation, metrics])
            self.assertLess(metrics["sameRowEdgeError"], 0.75, [orientation, metrics])
            self.assertLess(metrics["adjacentRowEdgeError"], 0.75, [orientation, metrics])

        check("vertical")
        check("horizontal")

    def test_tonic_change_updates_title_and_current_note(self):
        self.page.select_option('[data-testid="tonic-select"]', "5")
        self.assertIn("F Major", self.page.locator("#stateTitle").inner_text())
        self.assertNotEqual("", self.page.locator('[data-testid="current-note"]').inner_text())

    def test_stepper_advances_readout(self):
        before = self.page.locator('[data-testid="step-readout"]').inner_text()
        self.page.locator('[data-testid="next-step"]').click()
        after = self.page.locator('[data-testid="step-readout"]').inner_text()
        self.assertNotEqual(before, after)

    def test_audio_controls_are_present_and_clickable(self):
        self.assertTrue(self.page.locator('[data-testid="tone-select"]').is_visible())
        self.assertIn("Audio:", self.page.locator('[data-testid="audio-status"]').inner_text())
        self.page.select_option('[data-testid="tone-select"]', "muted_pluck")
        self.page.locator('[data-testid="test-audio"]').click()
        self.page.locator('[data-testid="test-audio"]').click()
        self.page.locator('[data-testid="play-scale"]').click()
        self.assertIn("Audio:", self.page.locator('[data-testid="audio-status"]').inner_text())

    def test_center_root_selector_defaults_to_centered_root(self):
        options = self.page.locator('[data-testid="root-select"] option')
        self.assertGreaterEqual(options.count(), 2)
        first_text = options.nth(0).inner_text()
        self.assertIn("C", first_text)
        before = self.page.locator('[data-testid="current-note"]').inner_text()
        self.page.select_option('[data-testid="root-select"]', index=1)
        after = self.page.locator('[data-testid="current-note"]').inner_text()
        self.assertNotEqual(before, "")
        self.assertIn("C", after)

    def test_practice_path_stays_on_inner_two_note_chains(self):
        labels = self.page.evaluate("""() => {
          return [...document.querySelectorAll('.key.in-path')]
            .sort((a, b) => Number(a.dataset.pathIndex) - Number(b.dataset.pathIndex))
            .map((key) => key.getAttribute('aria-label'));
        }""")
        self.assertEqual(labels, ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"])

    def test_regression_practice_lights_only_two_exquis_chains(self):
        lit = self.page.evaluate("""() => {
          return [...document.querySelectorAll('.key.hardware-lit')].map((key) => {
            return {
              id: key.dataset.cellId,
              lane: key.dataset.chainLane,
              row: Number(key.dataset.cellId.match(/r(\\d+)c/)[1]),
              isPath: key.classList.contains('in-path'),
              isTonic: key.classList.contains('tonic')
            };
          });
        }""")
        rows = {}
        for cell in lit:
            rows[cell["row"]] = rows.get(cell["row"], 0) + 1
        self.assertGreaterEqual(len(lit), 20)
        self.assertLessEqual(len(lit), 22)
        self.assertEqual({cell["lane"] for cell in lit}, {"0", "1"})
        self.assertEqual(set(rows.values()), {2})

    def test_regression_hardware_lit_keys_are_all_in_selected_key(self):
        pcs = self.page.evaluate("""() => {
          return [...document.querySelectorAll('.key.hardware-lit')].map((key) => Number(key.dataset.pc));
        }""")
        c_major = {0, 2, 4, 5, 7, 9, 11}
        self.assertGreaterEqual(len(pcs), 20)
        self.assertTrue(all(pc in c_major for pc in pcs))

    def test_regression_default_c_major_leds_match_product_photo(self):
        lit = self.page.evaluate("""() => [...document.querySelectorAll('.key.hardware-lit')]
          .map((key) => key.dataset.cellId)
          .sort((a, b) => {
            const ma = a.match(/r(\\d+)c(\\d+)/);
            const mb = b.match(/r(\\d+)c(\\d+)/);
            return Number(ma[1]) - Number(mb[1]) || Number(ma[2]) - Number(mb[2]);
          })""")
        self.assertEqual(lit, [
            "r0c2", "r0c3",
            "r1c1", "r1c3",
            "r2c2", "r2c4",
            "r3c1", "r3c3",
            "r4c2", "r4c4",
            "r5c2", "r5c3",
            "r6c2", "r6c4",
            "r7c2", "r7c3",
            "r8c2", "r8c4",
            "r9c2", "r9c4",
            "r10c2", "r10c4",
        ])

    def test_regression_all_c_keys_are_tonic_in_default_c_major(self):
        model = self.page.evaluate("""() => {
          const keys = [...document.querySelectorAll('.key')].map((key) => ({
            id: key.dataset.cellId,
            pc: Number(key.dataset.pc),
            label: key.getAttribute('aria-label'),
            tonic: key.classList.contains('tonic')
          }));
          return {
            cKeys: keys.filter((key) => key.pc === 0),
            nonCMarkedTonic: keys.filter((key) => key.pc !== 0 && key.tonic)
          };
        }""")
        self.assertGreaterEqual(len(model["cKeys"]), 5)
        self.assertTrue(all(item["tonic"] for item in model["cKeys"]), model["cKeys"])
        self.assertEqual(model["nonCMarkedTonic"], [])

    def test_regression_fingering_labels_only_two_lit_chains(self):
        labels = self.page.evaluate("""() => {
          return [...document.querySelectorAll('.key .finger')].map((finger) => {
            const key = finger.closest('.key');
            return {
              id: key.dataset.cellId,
              index: Number(key.dataset.pathIndex),
              finger: finger.textContent.trim(),
              lane: key.dataset.chainLane,
              lit: key.classList.contains('hardware-lit') || key.classList.contains('in-path') || key.classList.contains('tonic')
            };
          }).sort((a, b) => a.index - b.index);
        }""")
        self.assertEqual(len(labels), 8)
        self.assertEqual([label["finger"] for label in labels], ["Pink", "Ring", "Ring", "Mid", "Mid", "In", "In", "In"])
        self.assertTrue(all(label["lit"] for label in labels))

    def test_regression_natural_clusters_is_default_fingering_strategy(self):
        self.assertEqual(self.page.locator('[data-testid="strategy-select"]').input_value(), "natural_clusters")
        self.assertIn("Natural clusters", self.page.locator("#stateSubtitle").inner_text())
        self.assertIn("index handle the upper cluster", self.page.locator("#fingerRule").inner_text())

    def test_hand_selector_changes_fingering_overlay(self):
        self.assertIn("Left hand", self.page.locator("#stateSubtitle").inner_text())
        left_finger = self.page.locator(".finger").first.inner_text()
        self.page.select_option('[data-testid="hand-select"]', "right")
        self.assertIn("Right hand", self.page.locator("#stateSubtitle").inner_text())
        right_finger = self.page.locator(".finger").first.inner_text()
        self.assertNotEqual(left_finger, right_finger)

    def test_regression_wrist_led_pairs_allow_same_finger_for_d3_e3(self):
        self.page.select_option('[data-testid="strategy-select"]', "wrist_pairs")
        model = self.page.evaluate("""() => [...document.querySelectorAll('.key.in-path')]
          .sort((a, b) => Number(a.dataset.pathIndex) - Number(b.dataset.pathIndex))
          .map((key) => ({
            label: key.getAttribute('aria-label'),
            finger: key.querySelector('.finger') ? key.querySelector('.finger').textContent.trim() : '',
            cellId: key.dataset.cellId
        }))""")
        self.assertEqual([step["label"] for step in model[:4]], ["C3", "D3", "E3", "F3"])
        self.assertEqual(model[1]["finger"], "Ring")
        self.assertEqual(model[2]["finger"], "Ring")
        self.page.locator('[data-testid="next-step"]').click()
        self.assertEqual(self.page.locator('[data-testid="current-note"]').inner_text(), "D3")
        self.assertIn("may cover a pair", self.page.locator('[data-testid="finger-reason"]').inner_text())
        self.assertIn("wrist moves the hand", self.page.locator('[data-testid="finger-reason"]').inner_text())
        self.assertIn("wrist carry this pair", self.page.locator('[data-testid="motion-reason"]').inner_text())

    def test_regression_natural_clusters_prioritize_human_finger_names(self):
        self.page.select_option('[data-testid="strategy-select"]', "natural_clusters")
        model = self.page.evaluate("""() => [...document.querySelectorAll('.key.in-path')]
          .sort((a, b) => Number(a.dataset.pathIndex) - Number(b.dataset.pathIndex))
          .map((key) => ({
            label: key.getAttribute('aria-label'),
            finger: key.querySelector('.finger') ? key.querySelector('.finger').textContent.trim() : '',
            aria: key.querySelector('.finger') ? key.querySelector('.finger').getAttribute('aria-label') : ''
          }))""")
        self.assertEqual([step["label"] for step in model], ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"])
        self.assertEqual([step["finger"] for step in model], ["Pink", "Ring", "Ring", "Mid", "Mid", "In", "In", "In"])
        self.assertEqual([step["aria"] for step in model], ["Pinky (5)", "Ring (4)", "Ring (4)", "Middle (3)", "Middle (3)", "Index (2)", "Index (2)", "Index (2)"])
        self.assertIn("Natural clusters", self.page.locator("#stateSubtitle").inner_text())
        self.assertIn("pinky", self.page.locator("#fingerRule").inner_text())
        self.assertIn("index handle the upper cluster", self.page.locator("#fingerRule").inner_text())
        self.assertIn("Pinky (5)", self.page.locator('[data-testid="target-finger"]').inner_text())
        self.assertIn("hand cluster", self.page.locator('[data-testid="finger-reason"]').inner_text())

    def test_exercise_selector_defaults_to_root_octave_practice(self):
        self.assertEqual(self.page.locator('[data-testid="exercise-select"]').input_value(), "root_octave")
        self.assertIn("Root to octave", self.page.locator("#stateSubtitle").inner_text())
        self.assertIn("centered root-to-octave", self.page.locator('[data-testid="drill-prompt"]').inner_text())

    def test_mode_selector_defaults_to_practice(self):
        self.assertEqual(self.page.locator('[data-testid="mode-select"]').input_value(), "practice")
        self.assertTrue(self.page.locator('[data-testid="mode-switch"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="practice-mode"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="play-mode"]').is_visible())
        self.assertEqual(self.page.locator('[data-testid="practice-mode"]').get_attribute("aria-pressed"), "true")
        self.assertEqual(self.page.locator('[data-testid="play-mode"]').get_attribute("aria-pressed"), "false")
        self.assertEqual(self.page.locator('[data-testid="keyboard"]').get_attribute("data-mode"), "practice")
        self.assertIn("Practice:", self.page.locator("#stateSubtitle").inner_text())

    def test_regression_practice_mode_shows_actionable_targets(self):
        self.assertEqual(self.page.locator(".key.current").count(), 1)
        self.assertGreater(self.page.locator(".key.in-path .finger").count(), 5)
        self.assertGreater(self.page.locator(".key.dimmed").count(), 20)
        self.assertIn("Scale degree 1", self.page.locator("#currentDegree").inner_text())
        self.assertEqual(self.page.locator('[data-testid="target-finger"]').inner_text(), "Pinky (5)")
        self.assertEqual(self.page.locator('[data-testid="target-step"]').inner_text(), "Step 1 of 8")
        self.assertEqual(self.page.locator('[data-testid="path-chip"]').count(), 8)
        self.assertEqual(self.page.locator('[data-testid="path-chip"]').first.inner_text(), "1 C3")
        self.assertEqual(self.page.locator('[data-testid="path-chip"]').first.get_attribute("aria-label"), "Step 1 C3 Pinky (5)")

    def test_regression_practice_mode_explains_button_finger_motion_choices(self):
        self.assertTrue(self.page.locator('[data-testid="target-rationale"]').is_visible())
        self.assertIn("Exact C3", self.page.locator('[data-testid="button-reason"]').inner_text())
        self.assertIn("duplicates -> two-chain, then center", self.page.locator('[data-testid="button-reason"]').inner_text())
        self.assertIn("hand cluster", self.page.locator('[data-testid="finger-reason"]').inner_text())
        self.assertIn("index-led top", self.page.locator('[data-testid="finger-reason"]').inner_text())
        self.assertIn("no reaching", self.page.locator('[data-testid="motion-reason"]').inner_text())
        for _ in range(4):
            self.page.locator('[data-testid="next-step"]').click()
        self.assertEqual(self.page.locator('[data-testid="current-note"]').inner_text(), "G3")
        self.assertIn("Anchor the hand shape", self.page.locator('[data-testid="motion-reason"]').inner_text())
        self.assertIn("no reaching", self.page.locator('[data-testid="motion-reason"]').inner_text())

    def test_regression_practice_mode_scores_ergonomic_movement_load(self):
        self.assertIn("Movement load: low", self.page.locator('[data-testid="ergonomic-reason"]').inner_text())
        self.assertEqual(self.page.locator('[data-testid="ergonomic-reason"]').get_attribute("data-load-level"), "low")
        self.page.select_option('[data-testid="strategy-select"]', "natural_clusters")
        for _ in range(2):
            self.page.locator('[data-testid="next-step"]').click()
        load_text = self.page.locator('[data-testid="ergonomic-reason"]').inner_text()
        self.assertIn("Movement load:", load_text)
        self.assertIn("same ring", load_text)
        self.assertIn("pressure risk", load_text)
        self.assertIn(self.page.locator('[data-testid="ergonomic-reason"]').get_attribute("data-load-level"), {"medium", "high"})
        for _ in range(2):
            self.page.locator('[data-testid="next-step"]').click()
        self.assertIn("hand shift", self.page.locator('[data-testid="ergonomic-reason"]').inner_text())

    def test_regression_ergonomic_model_extends_to_other_keys_and_modes(self):
        cases = [
            ("2", "dorian", "D Dorian", ["D3", "E3", "F3", "G3", "A3", "B3", "C4", "D4"]),
            ("7", "mixolydian", "G Mixolydian", ["G3", "A3", "B3", "C4", "D4", "E4", "F4", "G4"]),
            ("10", "blues", "Bb Blues", ["Bb2", "Db3", "Eb3", "E3", "F3", "Ab3", "Bb3"]),
        ]
        for tonic, scale, title, expected_prefix in cases:
            with self.subTest(title=title):
                self.page.select_option('[data-testid="tonic-select"]', tonic)
                self.page.select_option('[data-testid="scale-select"]', scale)
                self.page.select_option('[data-testid="strategy-select"]', "natural_clusters")
                model = self.page.evaluate("""() => ({
                  title: document.querySelector('#stateTitle').textContent,
                  path: window.__exquisDebugSnapshot().currentPath.map((step) => ({
                    label: step.label,
                    midi: step.midi,
                    virtual: step.virtual
                  })),
                  fingers: [...document.querySelectorAll('.key.in-path')]
                    .sort((a, b) => Number(a.dataset.pathIndex) - Number(b.dataset.pathIndex))
                    .map((key) => key.querySelector('.finger') ? key.querySelector('.finger').textContent.trim() : ''),
                  load: document.querySelector('[data-testid="ergonomic-reason"]').textContent,
                  loadLevel: document.querySelector('[data-testid="ergonomic-reason"]').dataset.loadLevel
                })""")
                self.assertEqual(model["title"], title)
                self.assertEqual([step["label"] for step in model["path"]], expected_prefix)
                self.assertTrue(all(not step["virtual"] for step in model["path"]), model)
                self.assertEqual(model["fingers"], ["Pink", "Ring", "Ring", "Mid", "Mid", "In", "In", "In"][:len(expected_prefix)])
                self.assertIn("Movement load:", model["load"])
                self.assertIn(model["loadLevel"], {"low", "medium", "high"})

    def test_regression_two_octave_paths_extend_to_other_keys_and_modes(self):
        cases = [
            ("2", "dorian", ["D2", "E2", "F2", "G2", "A2", "B2", "C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4", "D4"]),
            ("7", "mixolydian", ["G2", "A2", "B2", "C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4", "D4", "E4", "F4", "G4"]),
            ("10", "blues", ["Bb1", "Db2", "Eb2", "E2", "F2", "Ab2", "Bb2", "Db3", "Eb3", "E3", "F3", "Ab3", "Bb3"]),
        ]
        for tonic, scale, expected_labels in cases:
            with self.subTest(tonic=tonic, scale=scale):
                self.page.select_option('[data-testid="tonic-select"]', tonic)
                self.page.select_option('[data-testid="scale-select"]', scale)
                self.page.select_option('[data-testid="exercise-select"]', "two_octaves")
                path = self.page.evaluate("() => window.__exquisDebugSnapshot().currentPath")
                self.assertEqual([step["label"] for step in path], expected_labels)
                self.assertTrue(all(not step["virtual"] for step in path), path)
                self.assertEqual(len({step["cellId"] for step in path}), len(path))
                self.assertTrue(all(path[index]["midi"] < path[index + 1]["midi"] for index in range(len(path) - 1)), path)

    def test_regression_ergonomic_model_covers_every_key_mode_octave(self):
        matrix = self.page.evaluate("""() => {
          const tonics = [...document.querySelectorAll('[data-testid="tonic-select"] option')].map((option) => option.value);
          const scales = [...document.querySelectorAll('[data-testid="scale-select"] option')].map((option) => option.value);
          const run = (tonic, scale, exercise, rootPick) => {
            document.querySelector('[data-testid="tonic-select"]').value = tonic;
            document.querySelector('[data-testid="tonic-select"]').dispatchEvent(new Event('change', { bubbles: true }));
            document.querySelector('[data-testid="scale-select"]').value = scale;
            document.querySelector('[data-testid="scale-select"]').dispatchEvent(new Event('change', { bubbles: true }));
            document.querySelector('[data-testid="exercise-select"]').value = exercise;
            document.querySelector('[data-testid="exercise-select"]').dispatchEvent(new Event('change', { bubbles: true }));
            document.querySelector('[data-testid="strategy-select"]').value = 'natural_clusters';
            document.querySelector('[data-testid="strategy-select"]').dispatchEvent(new Event('change', { bubbles: true }));
            const rootSelect = document.querySelector('[data-testid="root-select"]');
            const rootOptions = [...rootSelect.options].map((option) => ({
              value: option.value,
              label: option.textContent
            }));
            const candidates = [];
            for (const option of rootOptions) {
              rootSelect.value = option.value;
              rootSelect.dispatchEvent(new Event('change', { bubbles: true }));
              const candidatePath = window.__exquisDebugSnapshot().currentPath;
              const valid = candidatePath.length >= 2
                && candidatePath.every((step, index) => index === 0 || candidatePath[index - 1].midi < step.midi)
                && candidatePath.every((step) => !step.virtual);
              if (valid) {
                candidates.push({
                  value: option.value,
                  label: option.label,
                  firstMidi: candidatePath[0].midi,
                  length: candidatePath.length
                });
              }
            }
            candidates.sort((a, b) => (a.firstMidi - b.firstMidi) || (b.length - a.length));
            const chosen = rootPick === 'high' ? candidates[candidates.length - 1] : candidates[0];
            if (chosen) {
              rootSelect.value = chosen.value;
              rootSelect.dispatchEvent(new Event('change', { bubbles: true }));
            }
            const path = window.__exquisDebugSnapshot().currentPath;
            const keyIds = new Set([...document.querySelectorAll('[data-testid="exquis-key"]')].map((key) => key.dataset.cellId));
            const fingers = [...document.querySelectorAll('.key.in-path')]
              .sort((a, b) => Number(a.dataset.pathIndex) - Number(b.dataset.pathIndex))
              .map((key) => key.querySelector('.finger') ? key.querySelector('.finger').textContent.trim() : '');
            return {
              tonic,
              scale,
              exercise,
              rootPick,
              root: rootSelect.options[rootSelect.selectedIndex].textContent,
              candidateCount: candidates.length,
              path,
              fingers,
              load: document.querySelector('[data-testid="ergonomic-reason"]').textContent,
              loadLevel: document.querySelector('[data-testid="ergonomic-reason"]').dataset.loadLevel,
              allCellsExist: path.every((step) => keyIds.has(step.cellId)),
              ascending: path.every((step, index) => index === 0 || path[index - 1].midi < step.midi),
              uniqueCells: new Set(path.map((step) => step.cellId)).size === path.length,
              virtualCount: path.filter((step) => step.virtual).length
            };
          };
          const rows = [];
          for (const tonic of tonics) {
            for (const scale of scales) {
              rows.push(run(tonic, scale, 'root_octave', 'low'));
              rows.push(run(tonic, scale, 'root_octave', 'high'));
              rows.push(run(tonic, scale, 'two_octaves', 'low'));
            }
          }
          return rows;
        }""")
        self.assertEqual(len(matrix), 12 * 8 * 3)
        for row in matrix:
            with self.subTest(tonic=row["tonic"], scale=row["scale"], exercise=row["exercise"], rootPick=row["rootPick"]):
                natural_pattern = ["Pink", "Ring", "Ring", "Mid", "Mid", "In", "In", "In"]
                expected_fingers = [natural_pattern[index % len(natural_pattern)] for index in range(len(row["fingers"]))]
                self.assertGreater(row["candidateCount"], 0, row)
                self.assertGreaterEqual(len(row["path"]), 2, row)
                self.assertTrue(row["allCellsExist"], row)
                self.assertTrue(row["ascending"], row)
                self.assertEqual(row["virtualCount"], 0, row)
                self.assertEqual(row["fingers"], expected_fingers, row)
                self.assertIn("Movement load:", row["load"], row)
                self.assertIn(row["loadLevel"], {"low", "medium", "high"}, row)
                if row["exercise"] == "two_octaves":
                    self.assertTrue(row["uniqueCells"], row)
                    self.assertGreaterEqual(row["path"][-1]["midi"] - row["path"][0]["midi"], 12, row)

    def test_regression_practice_path_marks_hand_shift_steps(self):
        chips = self.page.locator('[data-testid="path-chip"]').evaluate_all("""els => els.map((el) => ({
          text: el.textContent.trim(),
          shift: el.classList.contains('shift-chip'),
          aria: el.getAttribute('aria-label')
        }))""")
        self.assertEqual([index + 1 for index, chip in enumerate(chips) if chip["shift"]], [5])
        self.assertIn("Shift hand", chips[4]["aria"])
        self.page.select_option('[data-testid="exercise-select"]', "two_octaves")
        two_octave_chips = self.page.locator('[data-testid="path-chip"]').evaluate_all("""els => els.map((el) => ({
          text: el.textContent.trim(),
          shift: el.classList.contains('shift-chip'),
          aria: el.getAttribute('aria-label')
        }))""")
        self.assertEqual([index + 1 for index, chip in enumerate(two_octave_chips) if chip["shift"]], [5, 9, 13])
        for index in [4, 8, 12]:
            self.assertIn("Shift hand", two_octave_chips[index]["aria"])

    def test_regression_practice_key_labels_are_explicit(self):
        root_id = self.page.locator('[data-testid="root-select"]').input_value()
        root_key = self.page.locator(f'[data-cell-id="{root_id}"]')
        self.assertEqual(root_key.locator(".degree-badge").inner_text(), "1")
        self.assertEqual(root_key.locator(".degree-badge").get_attribute("aria-label"), "Step 1")
        self.assertEqual(root_key.locator(".finger").inner_text(), "Pink")
        self.assertEqual(root_key.locator(".finger").get_attribute("aria-label"), "Pinky (5)")
        chips = self.page.locator('[data-testid="path-chip"]').evaluate_all("els => els.map((el) => el.textContent.trim())")
        self.assertEqual(chips, [
            "1 C3",
            "2 D3",
            "3 E3",
            "4 F3",
            "5 G3",
            "6 A3",
            "7 B3",
            "8 C4",
        ])

    def test_regression_practice_octaves_match_physical_play_labels(self):
        practice = self.page.evaluate("""() => [...document.querySelectorAll('.key.in-path')]
          .sort((a, b) => Number(a.dataset.pathIndex) - Number(b.dataset.pathIndex))
          .map((key) => ({ id: key.dataset.cellId, label: key.getAttribute('aria-label'), midi: Number(key.dataset.midi) }))""")
        self.page.locator('[data-testid="play-mode"]').click()
        play_by_id = self.page.evaluate("""() => Object.fromEntries([...document.querySelectorAll('[data-testid="exquis-key"]')]
          .map((key) => [key.dataset.cellId, { label: key.getAttribute('aria-label'), midi: Number(key.dataset.midi) }]))""")
        self.assertEqual([item["label"] for item in practice], ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"])
        self.assertEqual([item["midi"] for item in practice], [48, 50, 52, 53, 55, 57, 59, 60])
        self.assertEqual({item["id"] for item in practice}, {"r5c3", "r4c2", "r4c4", "r3c1", "r3c3", "r2c2", "r2c4", "r1c1"})
        for item in practice:
            self.assertEqual(item["label"], play_by_id[item["id"]]["label"], item)
            self.assertEqual(item["midi"], play_by_id[item["id"]]["midi"], item)

    def test_regression_duplicate_pitch_choices_prefer_centered_chain_cell(self):
        choices = self.page.evaluate("""() => {
          const keyboard = document.querySelector('[data-testid="keyboard"]').getBoundingClientRect();
          const center = { x: keyboard.left + keyboard.width / 2, y: keyboard.top + keyboard.height / 2 };
          const path = window.__exquisDebugSnapshot().currentPath;
          const allKeys = [...document.querySelectorAll('[data-testid="exquis-key"]')];
          return path.map((step) => {
            const sameMidi = allKeys.filter((key) => Number(key.dataset.midi) === step.midi);
            const chainOptions = sameMidi.filter((key) => key.dataset.chainLane !== '');
            const candidates = chainOptions.length ? chainOptions : sameMidi;
            const ranked = candidates.map((key) => {
              const rect = key.getBoundingClientRect();
              const x = rect.left + rect.width / 2;
              const y = rect.top + rect.height / 2;
              return {
                id: key.dataset.cellId,
                lane: key.dataset.chainLane || '',
                distance: Math.hypot(x - center.x, y - center.y)
              };
            }).sort((a, b) => a.distance - b.distance || a.id.localeCompare(b.id));
            return {
              label: step.label,
              selected: step.cellId,
              duplicateCount: sameMidi.length,
              bestCenteredChainCandidate: ranked[0].id
            };
          }).filter((item) => item.duplicateCount > 1);
        }""")
        self.assertGreaterEqual(len(choices), 2)
        for choice in choices:
            self.assertEqual(choice["selected"], choice["bestCenteredChainCandidate"], choice)

    def test_regression_play_path_audio_follows_visible_practice_order(self):
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ settings: { filter: {}, effects: {} } }]; },
              playNoteOnInstrument(midi, dur, inst, vel) { window.__ssliCalls.push(['play', midi, dur, inst, vel]); },
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; }
            }
          };
        }
        """)
        visible_midis = self.page.evaluate("""() => [...document.querySelectorAll('.key.in-path')]
          .sort((a, b) => Number(a.dataset.pathIndex) - Number(b.dataset.pathIndex))
          .map((key) => Number(key.dataset.midi))""")
        self.assertEqual(visible_midis, [48, 50, 52, 53, 55, 57, 59, 60])
        self.page.locator('[data-testid="play-scale"]').click()
        self.page.wait_for_function("() => window.__ssliCalls.filter((call) => call[0] === 'play').length >= 8", timeout=4000)
        played = self.page.evaluate("() => window.__ssliCalls.filter((call) => call[0] === 'play').map((call) => call[1]).slice(0, 8)")
        self.assertEqual(played, visible_midis)

    def test_regression_two_octave_exercise_uses_physical_two_octave_path(self):
        self.page.select_option('[data-testid="exercise-select"]', "two_octaves")
        expected_labels = ["C2", "D2", "E2", "F2", "G2", "A2", "B2", "C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"]
        expected_midis = [36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60]
        path = self.page.evaluate("""() => window.__exquisDebugSnapshot().currentPath""")
        chips = self.page.locator('[data-testid="path-chip"]').evaluate_all("els => els.map((el) => el.textContent.trim())")
        self.assertEqual(self.page.locator('[data-testid="root-select"] option:checked').inner_text(), "C2 / r9 k3")
        self.assertEqual(self.page.locator('[data-testid="step-readout"]').inner_text(), "1 / 15")
        self.assertEqual([step["label"] for step in path], expected_labels)
        self.assertEqual([step["midi"] for step in path], expected_midis)
        self.assertEqual(chips, [f"{index + 1} {label}" for index, label in enumerate(expected_labels)])
        self.assertTrue(all(not step["virtual"] for step in path))
        self.assertEqual(len({step["cellId"] for step in path}), len(path))
        self.assertTrue(all(path[index]["midi"] < path[index + 1]["midi"] for index in range(len(path) - 1)))
        self.page.locator('[data-testid="play-mode"]').click()
        play_by_id = self.page.evaluate("""() => Object.fromEntries([...document.querySelectorAll('[data-testid="exquis-key"]')]
          .map((key) => [key.dataset.cellId, { label: key.getAttribute('aria-label'), midi: Number(key.dataset.midi) }]))""")
        for step in path:
            self.assertEqual(step["label"], play_by_id[step["cellId"]]["label"], step)
            self.assertEqual(step["midi"], play_by_id[step["cellId"]]["midi"], step)

    def test_regression_two_octave_play_path_audio_follows_visible_order(self):
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ settings: { filter: {}, effects: {} } }]; },
              playNoteOnInstrument(midi, dur, inst, vel) { window.__ssliCalls.push(['play', midi, dur, inst, vel]); },
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; }
            }
          };
        }
        """)
        self.page.select_option('[data-testid="exercise-select"]', "two_octaves")
        visible_midis = self.page.evaluate("""() => [...document.querySelectorAll('.key.in-path')]
          .sort((a, b) => Number(a.dataset.pathIndex) - Number(b.dataset.pathIndex))
          .map((key) => Number(key.dataset.midi))""")
        self.assertEqual(visible_midis, [36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60])
        self.page.locator('[data-testid="play-scale"]').click()
        self.page.wait_for_function("() => window.__ssliCalls.filter((call) => call[0] === 'play').length >= 15", timeout=9000)
        played = self.page.evaluate("() => window.__ssliCalls.filter((call) => call[0] === 'play').map((call) => call[1]).slice(0, 15)")
        self.assertEqual(played, visible_midis)

    def test_regression_console_does_not_cover_two_octave_practice_keys(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        self.page.select_option('[data-testid="exercise-select"]', "two_octaves")
        overlaps = self.page.evaluate("""
        () => {
          const consoleRect = document.querySelector('[data-testid="console-panel"]').getBoundingClientRect();
          const keyboardRect = document.querySelector('[data-testid="keyboard"]').getBoundingClientRect();
          const intersects = (a, b) => a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
          const pathKeys = [...document.querySelectorAll('.key.in-path')].map((key) => ({
            id: key.dataset.cellId,
            rect: key.getBoundingClientRect()
          }));
          return {
            keyboard: intersects(consoleRect, keyboardRect),
            keys: pathKeys.filter((item) => intersects(consoleRect, item.rect)).map((item) => item.id)
          };
        }
        """)
        self.assertFalse(overlaps["keyboard"], overlaps)
        self.assertEqual(overlaps["keys"], [])

    def test_regression_exercise_selector_changes_actual_practice_path(self):
        before = self.page.evaluate("() => window.__exquisDebugSnapshot().currentPath.map((step) => step.label)")
        self.page.select_option('[data-testid="exercise-select"]', "inner_ladder")
        after = self.page.evaluate("() => window.__exquisDebugSnapshot().currentPath.map((step) => step.label)")
        self.assertEqual(before, ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"])
        self.assertEqual(after, ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4", "B3", "A3", "G3", "F3", "E3", "D3", "C3"])
        self.assertIn("1 / 15", self.page.locator('[data-testid="step-readout"]').inner_text())

    def test_regression_inner_chain_ladder_descends_same_two_chain_path(self):
        self.page.select_option('[data-testid="exercise-select"]', "inner_ladder")
        path = self.page.evaluate("""() => {
          const snapshot = window.__exquisDebugSnapshot().currentPath;
          const laneFor = (cellId) => document.querySelector(`[data-cell-id="${cellId}"]`).dataset.chainLane;
          return snapshot.map((step) => ({ label: step.label, cellId: step.cellId, lane: laneFor(step.cellId) }));
        }""")
        labels = [step["label"] for step in path]
        self.assertEqual(labels, labels[:8] + list(reversed(labels[:7])))
        self.assertEqual(path[0]["label"], "C3")
        self.assertEqual(path[7]["label"], "C4")
        self.assertEqual(path[-1]["label"], "C3")

    def test_regression_root_return_exercise_recenters_between_scale_tones(self):
        self.page.select_option('[data-testid="exercise-select"]', "root_returns")
        path = self.page.evaluate("() => window.__exquisDebugSnapshot().currentPath")
        labels = [step["label"] for step in path]
        cell_ids = [step["cellId"] for step in path]
        self.assertEqual(labels, ["C3", "D3", "C3", "E3", "C3", "F3", "C3", "G3", "C3", "A3", "C3", "B3", "C3", "C4"])
        self.assertEqual(cell_ids[0], cell_ids[2])
        self.assertEqual(cell_ids[0], cell_ids[4])
        self.assertEqual(cell_ids[0], cell_ids[6])
        self.assertIn("home reference", self.page.locator('[data-testid="drill-prompt"]').inner_text())

    def test_regression_play_mode_leaves_full_surface_available(self):
        self.page.locator('[data-testid="play-mode"]').click()
        self.assertEqual(self.page.locator('[data-testid="mode-select"]').input_value(), "play")
        self.assertEqual(self.page.locator('[data-testid="practice-mode"]').get_attribute("aria-pressed"), "false")
        self.assertEqual(self.page.locator('[data-testid="play-mode"]').get_attribute("aria-pressed"), "true")
        self.assertEqual(self.page.locator('[data-testid="keyboard"]').get_attribute("data-mode"), "play")
        self.assertIn("Play:", self.page.locator("#stateSubtitle").inner_text())
        self.assertIn("Free-play", self.page.locator('[data-testid="drill-prompt"]').inner_text())
        self.assertEqual(self.page.locator(".key.current").count(), 0)
        self.assertEqual(self.page.locator(".key.in-path").count(), 0)
        self.assertEqual(self.page.locator(".key .finger").count(), 0)
        self.assertEqual(self.page.locator('[data-testid="practice-path-strip"]').is_visible(), False)
        self.assertEqual(self.page.locator(".key.dimmed").count(), 0)
        self.assertIn("score paused", self.page.locator('[data-testid="drill-score"]').inner_text())

    def test_regression_play_mode_subtitle_hides_practice_scaffold(self):
        self.page.locator('[data-testid="play-mode"]').click()
        subtitle = self.page.locator("#stateSubtitle").inner_text()
        self.assertIn("Play:", subtitle)
        self.assertIn("full Exquis surface", subtitle)
        self.assertNotIn("Natural clusters", subtitle)
        self.assertNotIn("hand:", subtitle)
        self.assertNotIn("octave", subtitle.lower())

    def test_regression_practice_controls_are_hidden_in_play_mode(self):
        self.assertTrue(self.page.locator('[data-testid="exercise-control"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="practice-stepper"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="practice-target-panel"]').is_visible())
        self.page.locator('[data-testid="play-mode"]').click()
        for test_id in [
            "root-control",
            "hand-control",
            "exercise-control",
            "fingering-control",
            "view-control",
            "practice-stepper",
            "practice-target-panel",
            "drill-section",
            "practice-path-strip",
        ]:
            self.assertFalse(self.page.locator(f'[data-testid="{test_id}"]').is_visible(), test_id)
        self.assertTrue(self.page.locator('[data-testid="sound-engine-select"]').is_visible())

    def test_regression_practice_mode_shows_visible_hand_and_two_octave_controls(self):
        self.assertTrue(self.page.locator('[data-testid="left-hand-button"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="right-hand-button"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="lower-octave-button"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="higher-octave-button"]').is_visible())
        self.assertIn("Hand", self.page.locator('[data-testid="hand-control"]').inner_text())
        self.assertIn("Octave", self.page.locator('[data-testid="octave-control"]').inner_text())
        self.assertTrue(self.page.locator('[data-testid="exercise-button-root_octave"]').is_visible())
        two_octaves = self.page.locator('[data-testid="exercise-button-two_octaves"]')
        self.assertTrue(two_octaves.is_visible())
        self.assertEqual(two_octaves.inner_text(), "2 Oct")
        self.assertIn("Two octaves", two_octaves.get_attribute("aria-label"))
        self.assertEqual(self.page.locator('[data-testid="left-hand-button"]').get_attribute("aria-pressed"), "true")
        self.page.locator('[data-testid="right-hand-button"]').click()
        self.assertEqual(self.page.locator('[data-testid="hand-select"]').input_value(), "right")
        self.assertIn("Right hand", self.page.locator("#stateSubtitle").inner_text())
        two_octaves.click()
        self.assertEqual(self.page.locator('[data-testid="exercise-select"]').input_value(), "two_octaves")
        self.assertEqual(two_octaves.get_attribute("aria-pressed"), "true")
        self.assertIn("Two octaves", self.page.locator("#stateSubtitle").inner_text())
        self.assertGreaterEqual(self.page.locator('[data-testid="path-chip"]').count(), 13)

    def test_regression_hand_side_and_octave_side_are_deconflated(self):
        initial_path = self.page.evaluate("() => window.__exquisDebugSnapshot().currentPath.map((step) => step.label)")
        self.assertEqual(initial_path, ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"])
        self.assertEqual(self.page.locator('[data-testid="higher-octave-button"]').get_attribute("aria-pressed"), "true")
        self.page.locator('[data-testid="right-hand-button"]').click()
        right_hand_path = self.page.evaluate("() => window.__exquisDebugSnapshot().currentPath.map((step) => step.label)")
        self.assertEqual(right_hand_path, initial_path)
        self.assertIn("Right hand", self.page.locator("#stateSubtitle").inner_text())
        self.page.locator('[data-testid="lower-octave-button"]').click()
        lower_path = self.page.evaluate("() => window.__exquisDebugSnapshot().currentPath.map((step) => step.label)")
        self.assertEqual(self.page.locator('[data-testid="hand-select"]').input_value(), "right")
        self.assertEqual(self.page.locator('[data-testid="octave-select"]').input_value(), "lower")
        self.assertEqual(lower_path, ["C2", "D2", "E2", "F2", "G2", "A2", "B2", "C3"])
        self.assertEqual(self.page.locator('[data-testid="lower-octave-button"]').get_attribute("aria-pressed"), "true")
        self.page.locator('[data-testid="exercise-button-two_octaves"]').click()
        self.assertEqual(self.page.locator('[data-testid="lower-octave-button"]').get_attribute("aria-pressed"), "true")
        self.assertTrue(self.page.locator('[data-testid="lower-octave-button"]').is_disabled())
        self.assertTrue(self.page.locator('[data-testid="higher-octave-button"]').is_disabled())

    def test_regression_two_octave_keeps_resolved_octave_state_visible(self):
        self.page.locator('[data-testid="lower-octave-button"]').click()
        self.page.locator('[data-testid="exercise-button-two_octaves"]').click()
        self.assertTrue(self.page.locator('[data-testid="lower-octave-button"]').is_disabled())
        self.assertTrue(self.page.locator('[data-testid="higher-octave-button"]').is_disabled())
        self.assertEqual(self.page.locator('[data-testid="lower-octave-button"]').get_attribute("aria-pressed"), "true")
        self.assertEqual(self.page.locator('[data-testid="higher-octave-button"]').get_attribute("aria-pressed"), "false")

    def test_regression_practice_header_controls_do_not_overlap(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        overlaps = self.page.evaluate("""() => {
          const selectors = [
            '[data-testid="mode-switch"]',
            '[data-testid="tonic-select"]',
            '[data-testid="scale-select"]',
            '[data-testid="octave-buttons"]',
            '[data-testid="root-control"]',
            '[data-testid="hand-buttons"]',
            '[data-testid="exercise-buttons"]',
            '[data-testid="fingering-control"]',
            '[data-testid="view-control"]',
            '[data-testid="orientation-select"]',
            '[data-testid="rotate-surface"]'
          ];
          const boxes = selectors.map((selector) => {
            const el = document.querySelector(selector);
            const box = el.getBoundingClientRect();
            return { selector, left: box.left, right: box.right, top: box.top, bottom: box.bottom };
          });
          const collisions = [];
          for (let i = 0; i < boxes.length; i += 1) {
            for (let j = i + 1; j < boxes.length; j += 1) {
              const horizontal = Math.max(boxes[i].left, boxes[j].left) < Math.min(boxes[i].right, boxes[j].right);
              const vertical = Math.max(boxes[i].top, boxes[j].top) < Math.min(boxes[i].bottom, boxes[j].bottom);
              if (horizontal && vertical) collisions.push([boxes[i].selector, boxes[j].selector]);
            }
          }
          return collisions;
        }""")
        self.assertEqual(overlaps, [])

    def test_regression_practice_header_controls_follow_information_hierarchy(self):
        order = self.page.evaluate("""() => [...document.querySelector('.controls-grid').children].map((el) => (
          el.getAttribute('data-testid') || el.querySelector('[data-testid]')?.getAttribute('data-testid') || ''
        ))""")
        self.assertEqual(order, [
            "mode-switch",
            "tonic-select",
            "scale-select",
            "octave-control",
            "root-control",
            "hand-control",
            "exercise-control",
            "fingering-control",
            "view-control",
            "orientation-select",
            "rotate-surface",
        ])
        header_text = self.page.locator(".top-panel").inner_text()
        self.assertIn("Session", header_text)
        self.assertIn("Root Octave", header_text)
        self.assertIn("Start Button", header_text)
        self.assertIn("Finger Pattern", header_text)
        self.assertIn("Overlay", header_text)

    def test_regression_play_mode_midi_does_not_score_or_advance(self):
        self.page.evaluate("""
        () => {
          window.__mockPlayInput = { id: 'play-exquis', name: 'Exquis Play', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockPlayInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="play-mode"]').click()
        before_step = self.page.locator('[data-testid="step-readout"]').inner_text()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockPlayInput && window.__mockPlayInput.onmidimessage")
        self.page.evaluate("() => window.__mockPlayInput.onmidimessage({ data: [0x91, 48, 100] })")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-feedback\"]').textContent.includes('Play mode: C3')")
        self.assertEqual(self.page.locator('[data-testid="step-readout"]').inner_text(), before_step)
        self.assertIn("score paused", self.page.locator('[data-testid="drill-score"]').inner_text())
        self.assertEqual(self.page.locator('[data-testid="calibration-stats"]').inner_text(), "0 verified / 0 mismatched")
        self.assertGreater(self.page.locator(".midi-held").count(), 0)

    def test_regression_selected_root_keeps_first_fingering_assignment(self):
        root_id = self.page.locator('[data-testid="root-select"]').input_value()
        root_key = self.page.locator(f'[data-cell-id="{root_id}"]')
        self.assertEqual(root_key.locator(".degree-badge").inner_text(), "1")
        self.assertEqual(root_key.locator(".finger").inner_text(), "Pink")

    def test_regression_fingering_labels_are_valid_for_visible_path(self):
        fingers = self.page.locator(".key.in-path .finger").evaluate_all("els => els.map((el) => el.textContent.trim())")
        self.assertGreaterEqual(len(fingers), 5)
        for finger in fingers:
            self.assertIn(finger, {"Th", "In", "Mid", "Ring", "Pink"})

    def test_regression_scale_path_ascends_root_to_octave(self):
        path = self.page.evaluate("""() => [...document.querySelectorAll('.key.in-path')]
        .sort((a, b) => Number(a.dataset.pathIndex) - Number(b.dataset.pathIndex))
        .map((key) => ({
          midi: Number(key.dataset.midi),
          degree: key.querySelector('.degree-badge') ? key.querySelector('.degree-badge').textContent.trim() : '',
          finger: key.querySelector('.finger') ? key.querySelector('.finger').textContent.trim() : ''
        }))""")
        self.assertEqual([item["degree"] for item in path], ["1", "2", "3", "4", "5", "6", "7", "8"])
        self.assertEqual([item["finger"] for item in path], ["Pink", "Ring", "Ring", "Mid", "Mid", "In", "In", "In"])
        self.assertTrue(all(path[i]["midi"] < path[i + 1]["midi"] for i in range(len(path) - 1)))
        self.assertIn("1 / 8", self.page.locator('[data-testid="step-readout"]').inner_text())

    def test_regression_exquis_grid_octaves_match_c3_to_c4_practice_range(self):
        model = self.page.evaluate("""() => {
          const label = (id) => document.querySelector(`[data-cell-id="${id}"]`).getAttribute('aria-label');
          const path = [...document.querySelectorAll('.key.in-path')]
            .sort((a, b) => Number(a.dataset.pathIndex) - Number(b.dataset.pathIndex))
            .map((key) => key.getAttribute('aria-label'));
          const root = document.querySelector('[data-testid="root-select"]');
          return {
            middleCPhysicalCell: label('r5c3'),
            lowerCPhysicalCell: label('r8c2'),
            selectedRoot: root.options[root.selectedIndex].textContent,
            currentNote: document.querySelector('[data-testid="current-note"]').textContent,
            path
          };
        }""")
        self.assertEqual(model["middleCPhysicalCell"], "C3")
        self.assertEqual(model["lowerCPhysicalCell"], "C2")
        self.assertTrue(model["selectedRoot"].startswith("C3 /"))
        self.assertEqual(model["currentNote"], "C3")
        self.assertEqual(model["path"], ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"])

    def test_regression_octave_rollover_uses_chromatic_row_math(self):
        model = self.page.evaluate("""() => {
          const key = (id) => {
            const el = document.querySelector(`[data-cell-id="${id}"]`);
            return { label: el.getAttribute('aria-label'), midi: Number(el.dataset.midi) };
          };
          const row = (ids) => ids.map(key);
          return {
            row5: row(['r5c0', 'r5c1', 'r5c2', 'r5c3', 'r5c4']),
            row8: row(['r8c0', 'r8c1', 'r8c2', 'r8c3', 'r8c4', 'r8c5']),
            verticalStarts: row(['r10c0', 'r9c0', 'r8c0', 'r7c0', 'r6c0', 'r5c0'])
          };
        }""")
        self.assertEqual([item["label"] for item in model["row5"]], ["A2", "A#2", "B2", "C3", "C#3"])
        self.assertEqual([item["midi"] for item in model["row5"]], [45, 46, 47, 48, 49])
        self.assertEqual([item["label"] for item in model["row8"]], ["A#1", "B1", "C2", "C#2", "D2", "D#2"])
        self.assertEqual([item["midi"] for item in model["row8"]], [34, 35, 36, 37, 38, 39])
        vertical_deltas = [
            model["verticalStarts"][index + 1]["midi"] - model["verticalStarts"][index]["midi"]
            for index in range(len(model["verticalStarts"]) - 1)
        ]
        self.assertEqual(vertical_deltas, [4, 3, 4, 3, 4])

    def test_calibration_preview_mode_updates_guidance(self):
        self.page.select_option('[data-testid="view-select"]', "calibration")
        self.assertIn("Calibration preview", self.page.locator("#assumptionText").inner_text())
        self.assertEqual(self.page.locator(".calibration-target").count(), 1)

    def test_midi_unavailable_state_is_graceful(self):
        self.page.locator('[data-testid="enable-midi"]').click()
        status = self.page.locator('[data-testid="midi-status"]').inner_text()
        self.assertTrue("MIDI" in status)

    def test_regression_exquis_sysex_helpers_encode_official_root_scale_messages(self):
        payload = self.page.evaluate("""() => ({
          setup: window.__exquisSysexDebug.build(0x00, [window.__exquisSysexDebug.developerMask]),
          rootF: window.__exquisSysexDebug.build(0x06, [5]),
          scaleDorian: window.__exquisSysexDebug.build(0x07, [window.__exquisSysexDebug.exquisScaleNumberFor('dorian')]),
          scaleNaturalMinor: window.__exquisSysexDebug.build(0x07, [window.__exquisSysexDebug.exquisScaleNumberFor('aeolian')]),
          scaleMixolydian: window.__exquisSysexDebug.build(0x07, [window.__exquisSysexDebug.exquisScaleNumberFor('mixolydian')]),
          idForExquisFive: window.__exquisSysexDebug.scaleIdForExquisNumber(5),
          dorianDegrees: window.__exquisSysexDebug.degreesFor('dorian'),
          parsed: window.__exquisSysexDebug.parse([0xF0, 0x00, 0x21, 0x7E, 0x7F, 0x06, 0x05, 0xF7])
        })""")
        self.assertEqual(payload["setup"], [240, 0, 33, 126, 127, 0, 1, 247])
        self.assertEqual(payload["rootF"], [240, 0, 33, 126, 127, 6, 5, 247])
        self.assertEqual(payload["scaleDorian"], [240, 0, 33, 126, 127, 7, 1, 247])
        self.assertEqual(payload["scaleMixolydian"], [240, 0, 33, 126, 127, 7, 4, 247])
        self.assertEqual(payload["scaleNaturalMinor"], [240, 0, 33, 126, 127, 7, 5, 247])
        self.assertEqual(payload["idForExquisFive"], "aeolian")
        self.assertEqual(payload["dorianDegrees"], [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0])
        self.assertEqual(payload["parsed"]["command"], 6)
        self.assertEqual(payload["parsed"]["payload"], [5])

    def test_regression_exquis_key_mode_sync_uses_official_developer_sysex(self):
        self.page.evaluate("""
        () => {
          window.__sysexRequests = [];
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          window.__mockExquisOutput = {
            id: 'exquis-out',
            name: 'Exquis USB MIDI',
            manufacturer: 'Intuitive Instruments',
            sent: [],
            send(bytes) { this.sent.push([...bytes]); }
          };
          navigator.requestMIDIAccess = (opts) => {
            window.__sysexRequests.push(opts || {});
            return Promise.resolve({
              inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
              outputs: { forEach: (cb) => cb(window.__mockExquisOutput) },
              onstatechange: null
            });
          };
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="sync-exquis"]').click()
        self.page.select_option('[data-testid="tonic-select"]', "5")
        self.page.select_option('[data-testid="scale-select"]', "dorian")
        self.page.wait_for_timeout(140)
        sent = self.page.evaluate("() => window.__mockExquisOutput.sent")
        self.assertEqual(self.page.evaluate("() => window.__sysexRequests[0].sysex"), True)
        self.assertIn([240, 0, 33, 126, 127, 0, 1, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 0, 0, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 6, 0, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 6, 5, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 7, 1, 247], sent)
        self.assertNotIn([240, 0, 33, 126, 127, 1, 8, 247], sent)
        self.assertNotIn([240, 0, 33, 126, 127, 8, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 3, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 6, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 7, 247], sent)
        self.assertIn([240, 0, 33, 126, 247], sent)
        self.assertIn([240, 0, 33, 126, 4, 2, 29, 247], sent)
        self.assertIn([240, 0, 33, 126, 7, 2, 127, 95, 63, 247], sent)
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xF0, 0x00, 0x21, 0x7E, 0xF7] })")
        echo_count = self.page.evaluate("() => window.__mockExquisOutput.sent.length")
        self.page.wait_for_timeout(140)
        self.assertEqual(self.page.evaluate("() => window.__mockExquisOutput.sent.length"), echo_count)
        self.page.select_option('[data-testid="legacy-map-select"]', "top_left")
        self.page.wait_for_timeout(60)
        remapped = self.page.evaluate("(before) => window.__mockExquisOutput.sent.slice(before)", echo_count)
        self.assertIn([240, 0, 33, 126, 4, 0, 62, 247], remapped)
        before_lights = self.page.evaluate("() => window.__mockExquisOutput.sent.length")
        self.page.select_option('[data-testid="legacy-light-select"]', "both")
        self.page.wait_for_timeout(60)
        light_messages = self.page.evaluate("(before) => window.__mockExquisOutput.sent.slice(before)", before_lights)
        self.assertIn([240, 0, 33, 126, 3, 3, 127, 95, 63, 247], light_messages)
        self.assertIn([240, 0, 33, 126, 7, 3, 127, 95, 63, 247], light_messages)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("Exquis legacy key/mode", log)
        self.assertIn("buttonColors=61 noteColors=0 noteMap=61", log)
        self.assertIn("sent F Dorian", self.page.locator('[data-testid="exquis-sync-status"]').inner_text())

    def test_regression_exquis_dial_listen_uses_settings_encoder_developer_mode_and_logs_dials(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          window.__mockExquisOutput = {
            id: 'exquis-out',
            name: 'Exquis USB MIDI',
            manufacturer: 'Intuitive Instruments',
            sent: [],
            send(bytes) { this.sent.push([...bytes]); }
          };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: (cb) => cb(window.__mockExquisOutput) },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="dial-listen"]').click()
        sent = self.page.evaluate("() => window.__mockExquisOutput.sent")
        self.assertIn([240, 0, 33, 126, 127, 0, 19, 247], sent)
        self.assertEqual(self.page.locator('[data-testid="dial-listen"]').get_attribute("aria-pressed"), "true")
        self.assertIn("pads + encoders + settings", self.page.locator('[data-testid="exquis-sync-status"]').inner_text())
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xBF, 110, 65] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xB0, 74, 12] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xB0, 42, 5] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xB0, 43, 8] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xB0, 22, 127] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xB0, 22, 0] })")
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("Exquis dial encoder=110 Encoder 1 delta=1 raw=65", log)
        self.assertIn("Exquis dial raw status=0xB0 channel=1 data=176,74,12", log)
        self.assertIn("Exquis settings Encoder 2 root value=5 note=F", log)
        self.assertIn("Exquis settings Encoder 3 scale-number=8", log)
        self.assertIn("Exquis settings Encoder 2 click value=127", log)
        self.assertEqual(self.page.locator('[data-testid="tonic-select"]').input_value(), "5")
        self.assertIn("hardware scale number 8", self.page.locator('[data-testid="exquis-sync-status"]').inner_text())
        self.page.locator('[data-testid="dial-listen"]').click()
        self.assertIn([240, 0, 33, 126, 127, 0, 0, 247], self.page.evaluate("() => window.__mockExquisOutput.sent"))

    def test_regression_exquis_native_probe_sweeps_official_write_masks(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          window.__mockExquisOutput = {
            id: 'exquis-out',
            name: 'Exquis USB MIDI',
            manufacturer: 'Intuitive Instruments',
            sent: [],
            send(bytes) { this.sent.push([...bytes]); }
          };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: (cb) => cb(window.__mockExquisOutput) },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.select_option('[data-testid="tonic-select"]', "5")
        self.page.select_option('[data-testid="scale-select"]', "dorian")
        self.page.locator('[data-testid="native-probe-exquis"]').click()
        self.page.wait_for_timeout(3100)
        sent = self.page.evaluate("() => window.__mockExquisOutput.sent")
        self.assertIn([240, 0, 33, 126, 127, 0, 1, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 0, 16, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 0, 17, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 0, 19, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 6, 5, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 7, 1, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 3, 247], sent)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("Exquis native probe started root=F scale=Dorian", log)
        self.assertIn("mask=0x10 settings", log)
        self.assertIn("mask=0x13 pads+encoders+settings", log)

    def test_regression_exquis_edge_controls_are_labeled_and_show_capture_state(self):
        labels = self.page.evaluate("""
        () => [...document.querySelectorAll('[data-testid="edge-control"]')].map((el) => ({
          id: el.dataset.edgeId,
          text: el.innerText,
          label: el.getAttribute('aria-label')
        }))
        """)
        text = "\n".join(item["text"] for item in labels)
        for expected in ["Settings", "Sound", "Record", "Loop", "Clips", "Play/Stop", "Down", "Up", "Undo", "Redo", "Encoder 1", "Encoder 2", "Encoder 3", "Encoder 4", "Slider"]:
            self.assertIn(expected, text)
        layout = self.page.evaluate("""
        () => ({
          encoders: [...document.querySelectorAll('[data-testid="edge-top-controls"] [data-testid="edge-control"]')].map((el) => el.dataset.edgeId),
          select: [...document.querySelectorAll('[data-testid="edge-select-group"] [data-testid="edge-control"]')].map((el) => el.dataset.edgeId),
          slider: [...document.querySelectorAll('[data-testid="edge-slider-group"] [data-testid="edge-control"]')].map((el) => el.dataset.edgeId),
          undo: [...document.querySelectorAll('[data-testid="edge-undo-group"] [data-testid="edge-control"]')].map((el) => el.dataset.edgeId),
          actions: [...document.querySelectorAll('[data-testid="edge-action-row"] [data-testid="edge-control"]')].map((el) => el.dataset.edgeId),
          topBeforeKeys: Boolean(document.querySelector('[data-testid="edge-top-controls"]').compareDocumentPosition(document.querySelector('[data-testid="keyboard"]')) & Node.DOCUMENT_POSITION_FOLLOWING),
          bottomAfterKeys: Boolean(document.querySelector('[data-testid="edge-bottom-controls"]').compareDocumentPosition(document.querySelector('[data-testid="keyboard"]')) & Node.DOCUMENT_POSITION_PRECEDING)
        })
        """)
        self.assertEqual(layout["encoders"], ["enc1", "enc2", "enc3", "enc4"])
        self.assertEqual(layout["select"], ["down", "up"])
        self.assertEqual(layout["slider"], ["slider"])
        self.assertEqual(layout["undo"], ["undo", "redo"])
        self.assertEqual(layout["actions"], ["settings", "sound", "record", "loop", "clips", "playStop"])
        self.assertTrue(layout["topBeforeKeys"], layout)
        self.assertTrue(layout["bottomAfterKeys"], layout)
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          window.__mockExquisOutput = {
            id: 'exquis-out',
            name: 'Exquis USB MIDI',
            manufacturer: 'Intuitive Instruments',
            sent: [],
            send(bytes) { this.sent.push([...bytes]); }
          };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: (cb) => cb(window.__mockExquisOutput) },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="dial-listen"]').click()
        self.assertIn("settings/sound", self.page.locator('[data-testid="edge-control-status"]').inner_text())
        self.assertGreaterEqual(self.page.locator('[data-edge-id="settings"].captured').count(), 1)
        self.assertGreaterEqual(self.page.locator('[data-edge-id="enc2"].captured').count(), 1)
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xB0, 42, 5] })")
        self.assertGreaterEqual(self.page.locator('[data-edge-id="enc2"].active').count(), 1)
        self.assertIn("5", self.page.locator('[data-edge-id="enc2"]').inner_text())

    def test_regression_exquis_edge_controls_follow_orientation_layout(self):
        def metrics_for(orientation):
            self.page.select_option('[data-testid="orientation-select"]', orientation)
            self.page.wait_for_timeout(80)
            return self.page.evaluate("""() => {
              const box = (sel) => document.querySelector(sel).getBoundingClientRect();
              const safeTop = Math.min(
                window.innerHeight,
                document.querySelector('[data-testid="console-panel"]').getBoundingClientRect().top,
                document.querySelector('[data-testid="build-version"]').getBoundingClientRect().top
              );
              return {
                top: box('[data-testid="edge-top-controls"]'),
                keyboard: box('[data-testid="keyboard"]'),
                bottom: box('[data-testid="edge-bottom-controls"]'),
                safeTop,
                pageY: document.documentElement.scrollHeight - document.documentElement.clientHeight
              };
            }""")

        vertical = metrics_for("vertical")
        self.assertLess(vertical["top"]["bottom"], vertical["keyboard"]["top"], vertical)
        self.assertGreater(vertical["bottom"]["top"], vertical["keyboard"]["bottom"], vertical)
        self.assertLessEqual(vertical["bottom"]["bottom"], vertical["safeTop"] - 4, vertical)
        self.assertLessEqual(vertical["pageY"], 1, vertical)
        self.assertLess(abs((vertical["top"]["left"] + vertical["top"]["right"]) / 2 - (vertical["keyboard"]["left"] + vertical["keyboard"]["right"]) / 2), vertical["keyboard"]["width"] * 0.18, vertical)

        horizontal = metrics_for("horizontal")
        self.assertLess(horizontal["bottom"]["right"], horizontal["keyboard"]["left"], horizontal)
        self.assertGreater(horizontal["top"]["left"], horizontal["keyboard"]["right"], horizontal)
        self.assertGreaterEqual(horizontal["top"]["width"], 118, horizontal)
        self.assertGreaterEqual(horizontal["bottom"]["width"], 72, horizontal)
        self.assertLessEqual(horizontal["bottom"]["width"], 92, horizontal)
        self.assertLess(abs((horizontal["top"]["top"] + horizontal["top"]["bottom"]) / 2 - (horizontal["keyboard"]["top"] + horizontal["keyboard"]["bottom"]) / 2), horizontal["keyboard"]["height"] * 0.28, horizontal)

    def test_regression_exquis_side_controls_rotate_in_physical_bottom_to_top_order(self):
        self.page.select_option('[data-testid="orientation-select"]', "vertical")
        self.page.wait_for_timeout(100)
        vertical = self.page.evaluate("""() => {
          const rect = (sel) => document.querySelector(sel).getBoundingClientRect();
          const keyboard = rect('[data-testid="keyboard"]');
          return {
            enc1: rect('[data-edge-id="enc1"] .edge-visual'),
            enc4: rect('[data-edge-id="enc4"] .edge-visual'),
            settings: rect('[data-edge-id="settings"] .edge-visual'),
            playStop: rect('[data-edge-id="playStop"] .edge-visual'),
            keyboard
          };
        }""")
        self.assertLess(vertical["enc1"]["bottom"], vertical["keyboard"]["top"], vertical)
        self.assertLess(vertical["enc1"]["left"], vertical["enc4"]["left"], vertical)
        self.assertGreater(vertical["settings"]["top"], vertical["keyboard"]["bottom"], vertical)
        self.assertLess(vertical["settings"]["left"], vertical["playStop"]["left"], vertical)

        self.page.locator('[data-testid="rotate-surface"]').click()
        self.page.wait_for_timeout(100)
        vertical_rotated = self.page.evaluate("""() => {
          const rect = (sel) => document.querySelector(sel).getBoundingClientRect();
          const keyboard = rect('[data-testid="keyboard"]');
          return {
            deviceRotation: document.querySelector('[data-testid="exquis-device"]').dataset.rotation,
            enc1: rect('[data-edge-id="enc1"] .edge-visual'),
            enc4: rect('[data-edge-id="enc4"] .edge-visual'),
            settings: rect('[data-edge-id="settings"] .edge-visual'),
            playStop: rect('[data-edge-id="playStop"] .edge-visual'),
            keyboard
          };
        }""")
        self.assertEqual(vertical_rotated["deviceRotation"], "180", vertical_rotated)
        self.assertGreater(vertical_rotated["enc1"]["top"], vertical_rotated["keyboard"]["bottom"], vertical_rotated)
        self.assertGreater(vertical_rotated["enc1"]["left"], vertical_rotated["enc4"]["left"], vertical_rotated)
        self.assertLess(vertical_rotated["settings"]["bottom"], vertical_rotated["keyboard"]["top"], vertical_rotated)
        self.assertGreater(vertical_rotated["settings"]["left"], vertical_rotated["playStop"]["left"], vertical_rotated)

        self.page.select_option('[data-testid="orientation-select"]', "horizontal")
        if self.page.locator('[data-testid="keyboard"]').get_attribute("data-rotation") != "0":
            self.page.locator('[data-testid="rotate-surface"]').click()
        self.page.wait_for_timeout(100)
        metrics = self.page.evaluate("""() => {
          const rect = (sel) => document.querySelector(sel).getBoundingClientRect();
          const keyboard = rect('[data-testid="keyboard"]');
          const controls = {
            settings: rect('[data-edge-id="settings"] .edge-visual'),
            sound: rect('[data-edge-id="sound"] .edge-visual'),
            record: rect('[data-edge-id="record"] .edge-visual'),
            loop: rect('[data-edge-id="loop"] .edge-visual'),
            clips: rect('[data-edge-id="clips"] .edge-visual'),
            playStop: rect('[data-edge-id="playStop"] .edge-visual'),
            down: rect('[data-edge-id="down"] .edge-visual'),
            up: rect('[data-edge-id="up"] .edge-visual'),
            slider: rect('[data-edge-id="slider"] .edge-visual'),
            undo: rect('[data-edge-id="undo"] .edge-visual'),
            redo: rect('[data-edge-id="redo"] .edge-visual'),
            enc1: rect('[data-edge-id="enc1"] .edge-visual'),
            enc2: rect('[data-edge-id="enc2"] .edge-visual'),
            enc3: rect('[data-edge-id="enc3"] .edge-visual'),
            enc4: rect('[data-edge-id="enc4"] .edge-visual')
          };
          const cx = (box) => (box.left + box.right) / 2;
          const cy = (box) => (box.top + box.bottom) / 2;
          return {
            keyboard,
            controls,
            leftRailIds: Object.keys(controls).filter((id) => controls[id].right < keyboard.left),
            rightRailIds: Object.keys(controls).filter((id) => controls[id].left > keyboard.right),
            leftOrder: Object.keys(controls)
              .filter((id) => controls[id].right < keyboard.left)
              .sort((a, b) => cy(controls[a]) - cy(controls[b])),
            rightOrder: Object.keys(controls)
              .filter((id) => controls[id].left > keyboard.right)
              .sort((a, b) => cy(controls[a]) - cy(controls[b])),
            actionMaxY: Math.max(cy(controls.settings), cy(controls.sound), cy(controls.record), cy(controls.loop), cy(controls.clips), cy(controls.playStop)),
            sliderY: cy(controls.slider),
            encoderMinY: Math.min(cy(controls.enc1), cy(controls.enc2), cy(controls.enc3), cy(controls.enc4))
          };
        }""")
        self.assertEqual(metrics["leftRailIds"], ["settings", "sound", "record", "loop", "clips", "playStop", "down", "up", "slider", "undo", "redo"], metrics)
        self.assertEqual(metrics["rightRailIds"], ["enc1", "enc2", "enc3", "enc4"], metrics)
        self.assertEqual(metrics["leftOrder"], ["settings", "sound", "record", "loop", "clips", "playStop", "down", "up", "slider", "undo", "redo"], metrics)
        self.assertEqual(metrics["rightOrder"], ["enc1", "enc2", "enc3", "enc4"], metrics)
        self.assertLess(metrics["actionMaxY"], metrics["sliderY"], metrics)
        self.assertLess(metrics["sliderY"], metrics["keyboard"]["bottom"], metrics)
        self.assertGreater(metrics["encoderMinY"], metrics["keyboard"]["top"], metrics)

        self.page.locator('[data-testid="rotate-surface"]').click()
        self.page.wait_for_timeout(100)
        rotated = self.page.evaluate("""() => {
          const rect = (sel) => document.querySelector(sel).getBoundingClientRect();
          const keyboard = rect('[data-testid="keyboard"]');
          const controls = {
            settings: rect('[data-edge-id="settings"] .edge-visual'),
            sound: rect('[data-edge-id="sound"] .edge-visual'),
            record: rect('[data-edge-id="record"] .edge-visual'),
            loop: rect('[data-edge-id="loop"] .edge-visual'),
            clips: rect('[data-edge-id="clips"] .edge-visual'),
            playStop: rect('[data-edge-id="playStop"] .edge-visual'),
            down: rect('[data-edge-id="down"] .edge-visual'),
            up: rect('[data-edge-id="up"] .edge-visual'),
            slider: rect('[data-edge-id="slider"] .edge-visual'),
            undo: rect('[data-edge-id="undo"] .edge-visual'),
            redo: rect('[data-edge-id="redo"] .edge-visual'),
            enc1: rect('[data-edge-id="enc1"] .edge-visual'),
            enc2: rect('[data-edge-id="enc2"] .edge-visual'),
            enc3: rect('[data-edge-id="enc3"] .edge-visual'),
            enc4: rect('[data-edge-id="enc4"] .edge-visual')
          };
          const cy = (box) => (box.top + box.bottom) / 2;
          return {
            deviceRotation: document.querySelector('[data-testid="exquis-device"]').dataset.rotation,
            keyboardRotation: document.querySelector('[data-testid="keyboard"]').dataset.rotation,
            encodersAreLeft: controls.enc1.right < keyboard.left,
            buttonsAreRight: controls.settings.left > keyboard.right,
            leftOrder: Object.keys(controls)
              .filter((id) => controls[id].right < keyboard.left)
              .sort((a, b) => cy(controls[a]) - cy(controls[b])),
            rightOrder: Object.keys(controls)
              .filter((id) => controls[id].left > keyboard.right)
              .sort((a, b) => cy(controls[a]) - cy(controls[b]))
          };
        }""")
        self.assertEqual(rotated["deviceRotation"], "180", rotated)
        self.assertEqual(rotated["keyboardRotation"], "180", rotated)
        self.assertTrue(rotated["encodersAreLeft"], rotated)
        self.assertTrue(rotated["buttonsAreRight"], rotated)
        self.assertEqual(rotated["leftOrder"], ["enc4", "enc3", "enc2", "enc1"], rotated)
        self.assertEqual(rotated["rightOrder"], ["redo", "undo", "slider", "up", "down", "playStop", "clips", "loop", "record", "sound", "settings"], rotated)

    def test_regression_exquis_hardware_controls_use_physical_shapes(self):
        self.page.select_option('[data-testid="orientation-select"]', "horizontal")
        self.page.wait_for_timeout(100)
        metrics = self.page.evaluate("""() => {
          const rect = (sel) => document.querySelector(sel).getBoundingClientRect();
          const radius = (sel) => getComputedStyle(document.querySelector(sel)).borderRadius;
          const knob = rect('[data-edge-id="enc1"] .edge-visual');
          const knobLabel = rect('[data-edge-id="enc1"] .edge-label');
          const action = rect('[data-edge-id="settings"] .edge-visual');
          const actionLabel = rect('[data-edge-id="settings"] .edge-label');
          const slider = rect('[data-edge-id="slider"] .edge-visual');
          const select = rect('[data-edge-id="down"] .edge-visual');
          const device = rect('[data-testid="exquis-device"]');
          const keyboard = rect('[data-testid="keyboard"]');
          return { knob, knobLabel, action, actionLabel, slider, select, device, keyboard, deviceRadius: radius('[data-testid="exquis-device"]') };
        }""")
        self.assertLessEqual(abs(metrics["knob"]["width"] - metrics["knob"]["height"]), 2, metrics)
        self.assertGreaterEqual(metrics["knob"]["width"], 44, metrics)
        self.assertGreater(metrics["knobLabel"]["left"], metrics["knob"]["right"], metrics)
        self.assertLessEqual(abs(metrics["action"]["width"] - metrics["action"]["height"]), 2, metrics)
        self.assertGreaterEqual(metrics["action"]["width"], 32, metrics)
        action_label_beside = metrics["actionLabel"]["left"] > metrics["action"]["right"]
        action_label_rotated = metrics["actionLabel"]["height"] > metrics["actionLabel"]["width"] * 1.4
        self.assertTrue(action_label_beside or action_label_rotated, metrics)
        self.assertGreater(metrics["slider"]["height"], metrics["slider"]["width"] * 1.8, metrics)
        self.assertLessEqual(abs(metrics["select"]["width"] - metrics["select"]["height"]), 4, metrics)
        self.assertLess(metrics["device"]["top"], metrics["keyboard"]["top"], metrics)
        self.assertGreater(metrics["device"]["bottom"], metrics["keyboard"]["bottom"], metrics)

    def test_regression_horizontal_hardware_slab_does_not_waste_vertical_space(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        self.page.select_option('[data-testid="orientation-select"]', "horizontal")
        self.page.wait_for_timeout(100)
        metrics = self.page.evaluate("""() => {
          const rect = (sel) => document.querySelector(sel).getBoundingClientRect();
          const device = rect('[data-testid="exquis-device"]');
          const keyboard = rect('[data-testid="keyboard"]');
          return {
            device,
            keyboard,
            topDead: keyboard.top - device.top,
            bottomDead: device.bottom - keyboard.bottom,
            keyboardShare: keyboard.height / device.height
          };
        }""")
        self.assertLessEqual(metrics["topDead"], 38, metrics)
        self.assertLessEqual(metrics["bottomDead"], 38, metrics)
        self.assertGreaterEqual(metrics["keyboardShare"], 0.82, metrics)

    def test_regression_horizontal_exquis_layout_fits_stage_without_dead_band_or_clipped_stepper(self):
        for width, height, min_key_width in [(1280, 720, 470), (1366, 768, 520), (1536, 864, 620), (1600, 900, 650)]:
            with self.subTest(viewport=(width, height)):
                self.page.set_viewport_size({"width": width, "height": height})
                self.page.select_option('[data-testid="orientation-select"]', "horizontal")
                self.page.wait_for_timeout(100)
                metrics = self.page.evaluate("""() => {
                  const rect = (sel) => document.querySelector(sel).getBoundingClientRect();
                  const stage = rect('.stage-panel');
                  const path = rect('[data-testid="practice-path-strip"]');
                  const stepper = rect('[data-testid="practice-stepper"]');
                  const encoderRail = document.querySelector('[data-testid="edge-top-controls"]').closest('.edge-controls').getBoundingClientRect();
                  const keyboard = rect('[data-testid="keyboard"]');
                  const bottomRail = document.querySelector('[data-testid="edge-bottom-controls"]').closest('.edge-controls').getBoundingClientRect();
                  const side = rect('.side-panel');
                  const safeTop = Math.min(
                    window.innerHeight,
                    document.querySelector('[data-testid="console-panel"]').getBoundingClientRect().top,
                    document.querySelector('[data-testid="build-version"]').getBoundingClientRect().top
                  );
                  const device = {
                    left: Math.min(encoderRail.left, keyboard.left, bottomRail.left),
                    right: Math.max(encoderRail.right, keyboard.right, bottomRail.right),
                    top: Math.min(encoderRail.top, keyboard.top, bottomRail.top),
                    bottom: Math.max(encoderRail.bottom, keyboard.bottom, bottomRail.bottom)
                  };
                  return {
                    stage,
                    path,
                    stepper,
                    device,
                    safeTop,
                    encoderRail,
                    bottomRail,
                    side,
                    keyboard,
                    pageX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
                    pageY: document.documentElement.scrollHeight - document.documentElement.clientHeight
                  };
                }""")
                self.assertLessEqual(metrics["stepper"]["right"], metrics["stage"]["right"] - 8, metrics)
                self.assertGreaterEqual(metrics["device"]["left"], metrics["stage"]["left"] + 8, metrics)
                self.assertLessEqual(metrics["device"]["right"], metrics["stage"]["right"] - 8, metrics)
                self.assertLessEqual(metrics["device"]["right"], metrics["side"]["left"] - 8, metrics)
                self.assertLessEqual(metrics["device"]["bottom"], metrics["safeTop"] - 4, metrics)
                self.assertLess(metrics["bottomRail"]["right"], metrics["keyboard"]["left"], metrics)
                self.assertGreater(metrics["encoderRail"]["left"], metrics["keyboard"]["right"], metrics)
                self.assertLessEqual(metrics["device"]["top"] - metrics["path"]["bottom"], 72, metrics)
                self.assertGreaterEqual(metrics["keyboard"]["width"], min_key_width, metrics)
                self.assertLessEqual(metrics["pageX"], 1, metrics)
                self.assertLessEqual(metrics["pageY"], 1, metrics)

    def test_regression_exquis_incoming_root_scale_sysex_updates_ui_without_echo(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          window.__mockExquisOutput = {
            id: 'exquis-out',
            name: 'Exquis USB MIDI',
            manufacturer: 'Intuitive Instruments',
            sent: [],
            send(bytes) { this.sent.push([...bytes]); }
          };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: (cb) => cb(window.__mockExquisOutput) },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="sync-exquis"]').click()
        before_count = self.page.evaluate("() => window.__mockExquisOutput.sent.length")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0xF0, 0x00, 0x21, 0x7E, 0x7F, 0x06, 0x02, 0xF7] });
          window.__mockExquisInput.onmidimessage({ data: [0xF0, 0x00, 0x21, 0x7E, 0x7F, 0x07, 0x01, 0xF7] });
        }
        """)
        self.assertEqual(self.page.locator('[data-testid="tonic-select"]').input_value(), "2")
        self.assertEqual(self.page.locator('[data-testid="scale-select"]').input_value(), "dorian")
        self.assertIn("D Dorian", self.page.locator("#stateTitle").inner_text())
        self.page.wait_for_timeout(140)
        after_count = self.page.evaluate("() => window.__mockExquisOutput.sent.length")
        self.assertGreater(after_count, before_count)
        sent_after = self.page.evaluate("(before) => window.__mockExquisOutput.sent.slice(before)", before_count)
        self.assertNotIn([240, 0, 33, 126, 127, 6, 2, 247], sent_after)
        self.assertNotIn([240, 0, 33, 126, 127, 7, 1, 247], sent_after)
        self.assertIn([240, 0, 33, 126, 247], sent_after)

    def test_regression_exquis_sync_falls_back_to_input_only_when_sysex_permission_denied(self):
        self.page.evaluate("""
        () => {
          window.__requests = [];
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = (opts) => {
            window.__requests.push(opts || {});
            if (opts && opts.sysex) return Promise.reject(new Error('sysex denied'));
            return Promise.resolve({
              inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
              outputs: { forEach: () => {} },
              onstatechange: null
            });
          };
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.assertEqual(self.page.evaluate("() => window.__requests.map(r => !!r.sysex)"), [True, False])
        self.assertTrue(self.page.locator('[data-testid="sync-exquis"]').is_disabled())
        self.assertIn("SysEx permission unavailable", self.page.locator('[data-testid="exquis-sync-status"]').inner_text())

    def test_regression_exquis_probe_sends_official_and_legacy_diagnostics(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          window.__mockExquisOutput = {
            id: 'exquis-out',
            name: 'Exquis USB MIDI',
            manufacturer: 'Intuitive Instruments',
            sent: [],
            send(bytes) { this.sent.push([...bytes]); }
          };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: (cb) => cb(window.__mockExquisOutput) },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="probe-exquis"]').click()
        self.page.wait_for_timeout(1050)
        sent = self.page.evaluate("() => window.__mockExquisOutput.sent")
        self.assertIn([240, 126, 127, 6, 1, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 0, 32, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 0, 63, 247], sent)
        self.assertIn([240, 0, 33, 126, 247], sent)
        self.assertIn([240, 0, 33, 126, 4, 0, 60, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 0, 0, 247], sent)
        self.page.evaluate("""
        () => window.__mockExquisInput.onmidimessage({ data: [0xF0, 0x7E, 0x7F, 0x06, 0x02, 0x00, 0x21, 0x7E, 0x01, 0x02, 0xF7] })
        """)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("raw SysEx receive bytes=F0 7E 7F 06 02 00 21 7E 01 02 F7", log)
        self.assertIn("universal identity response payload=0,33,126,1,2", log)
        self.assertIn("identity response received", self.page.locator('[data-testid="exquis-sync-status"]').inner_text())

    def test_clear_calibration_button_resets_stats(self):
        self.assertFalse(self.page.locator('[data-testid="clear-calibration"]').is_visible())
        self.page.locator('[data-testid="clear-calibration"]').evaluate("el => el.click()")
        self.assertEqual(self.page.locator('[data-testid="calibration-stats"]').inner_text(), "0 verified / 0 mismatched")

    def test_mock_midi_note_marks_calibration(self):
        self.page.evaluate("""
        () => {
          window.__mockMidiInput = { id: 'exquis-mock', name: 'Exquis Mock', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockMidiInput) },
            outputs: { forEach: () => {} }
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockMidiInput && window.__mockMidiInput.onmidimessage")
        self.assertIn("Exquis Mock", self.page.locator('[data-testid="midi-input-select"]').inner_text())
        self.assertIn("Exquis Mock", self.page.locator('[data-testid="midi-devices"]').inner_text())
        target_midi = self.page.locator(".key.current").get_attribute("data-midi")
        self.page.evaluate("""
        (midi) => {
          window.__mockMidiInput.onmidimessage({ data: [0x90, Number(midi), 100] });
        }
        """, target_midi)
        self.assertIn("Correct", self.page.locator('[data-testid="coach-feedback"]').inner_text())
        self.assertIn("note-on", self.page.locator('[data-testid="midi-activity"]').inner_text())
        self.assertIn("1 correct", self.page.locator('[data-testid="drill-score"]').inner_text())
        self.assertEqual(self.page.locator('[data-testid="calibration-stats"]').inner_text(), "1 verified / 0 mismatched")

    def test_exquis_mpe_note_sequence_scores_and_advances(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")

        first_midi = self.page.locator(".key.current").get_attribute("data-midi")
        self.page.evaluate("""
        (midi) => {
          window.__mockExquisInput.onmidimessage({ data: [0x91, Number(midi), 108] });
        }
        """, first_midi)
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"drill-score\"]').textContent.includes('1 correct')")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"step-readout\"]').textContent.startsWith('2 /')")

        second_midi = self.page.locator(".key.current").get_attribute("data-midi")
        self.page.evaluate("""
        (midi) => {
          window.__mockExquisInput.onmidimessage({ data: [0x92, Number(midi), 96] });
        }
        """, second_midi)
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"drill-score\"]').textContent.includes('2 correct')")
        self.assertIn("streak 2", self.page.locator('[data-testid="drill-score"]').inner_text())
        self.assertIn("note-on", self.page.locator('[data-testid="midi-activity"]').inner_text())

        wrong_midi = (int(second_midi) + 1) % 127
        self.page.evaluate("""
        (midi) => {
          window.__mockExquisInput.onmidimessage({ data: [0x93, midi, 84] });
        }
        """, wrong_midi)
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"drill-score\"]').textContent.includes('1 missed')")
        self.assertIn("streak 0", self.page.locator('[data-testid="drill-score"]').inner_text())

    def test_exquis_midi_note_tracks_touch_pressure_and_note_off(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Microsoft Corporation', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 63] })")
        self.page.wait_for_function("() => document.querySelectorAll('.midi-held').length > 0")
        self.assertIn("C3", self.page.locator('[data-testid="last-midi"]').inner_text())
        self.assertIn("note-on C3", self.page.locator('[data-testid="diagnostic-log"]').inner_text())
        self.assertIn("raw=48", self.page.locator('[data-testid="diagnostic-log"]').inner_text())
        self.assertIn("MIDI voice start C3", self.page.locator('[data-testid="diagnostic-log"]').inner_text())
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xD1, 90] })")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('channel-pressure C3 pressure=90')")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xA1, 48, 110] })")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('poly-aftertouch C3 pressure=110')")
        pressure_value = self.page.locator(".midi-held").first.evaluate("el => getComputedStyle(el).getPropertyValue('--midi-pressure')")
        self.assertGreater(float(pressure_value), 0.8)
        self.page.wait_for_timeout(1000)
        self.assertIn("C3", self.page.locator('[data-testid="last-midi"]').inner_text())
        self.assertGreater(self.page.locator(".midi-held").count(), 0)
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x81, 48, 0] })")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"midi-activity\"]').textContent.includes('note-off')")
        self.assertIn("C3", self.page.locator('[data-testid="last-midi"]').inner_text())
        self.assertEqual(self.page.locator(".midi-held").count(), 0)

    def test_regression_midi_highlight_matches_exact_note_only(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90, 60, 96] })")
        self.page.wait_for_function("() => document.querySelectorAll('.midi-held').length === 1")
        lit = self.page.evaluate("""() => [...document.querySelectorAll('.midi-held, .midi-held-pitch, .midi-hit, .midi-pitch')].map((el) => ({
          id: el.dataset.cellId,
          midi: Number(el.dataset.midi),
          label: el.getAttribute('aria-label'),
          classes: el.className
        }))""")
        self.assertEqual([item["midi"] for item in lit], [60], lit)
        self.assertEqual([item["id"] for item in lit], ["r2c5"], lit)
        self.assertFalse(any("midi-held-pitch" in item["classes"] or "midi-pitch" in item["classes"] for item in lit), lit)
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xA0, 60, 111] })")
        aftertouch_lit = self.page.evaluate("""() => [...document.querySelectorAll('.midi-held, .midi-held-pitch, .midi-hit, .midi-pitch')].map((el) => ({
          id: el.dataset.cellId,
          midi: Number(el.dataset.midi),
          label: el.getAttribute('aria-label'),
          classes: el.className
        }))""")
        self.assertEqual([item["midi"] for item in aftertouch_lit], [60], aftertouch_lit)
        self.assertFalse(any(item["midi"] != 60 or item["label"] != "C4" for item in aftertouch_lit), aftertouch_lit)
        self.assertFalse(any("pitch" in item["classes"] for item in aftertouch_lit), aftertouch_lit)
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x80, 60, 0] })")
        self.page.wait_for_function("() => document.querySelectorAll('.midi-held, .midi-held-pitch, .midi-hit, .midi-pitch').length === 0")

    def test_ui_key_press_generates_audio_and_releases(self):
        first_key = self.page.locator('[data-testid="exquis-key"]').first
        midi = first_key.get_attribute("data-midi")
        box = first_key.bounding_box()
        self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        self.page.mouse.down()
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('key down')")
        self.assertGreater(self.page.locator(".midi-held, .midi-held-pitch").count(), 0)
        self.assertIn("MIDI voice start", self.page.locator('[data-testid="diagnostic-log"]').inner_text())
        self.assertIn("midi=" + midi, self.page.locator('[data-testid="diagnostic-log"]').inner_text())
        self.page.mouse.up()
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('released all UI keys') || document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('key up')")
        self.assertEqual(self.page.locator(".midi-held, .midi-held-pitch").count(), 0)

    def test_guide_audio_creates_output_graph(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__audioEvents = [];
          class FakeParam {
            constructor(name) {
              this.name = name;
              this.value = 0;
            }
            setValueAtTime(value, time) {
              this.value = value;
              window.__audioEvents.push(['setValueAtTime', this.name, value, time]);
            }
            exponentialRampToValueAtTime(value, time) {
              this.value = value;
              window.__audioEvents.push(['exponentialRampToValueAtTime', this.name, value, time]);
            }
          }
          class FakeNode {
            constructor(kind) {
              this.kind = kind;
              this.gain = new FakeParam(kind + '.gain');
              this.frequency = new FakeParam(kind + '.frequency');
              this.Q = { value: 0 };
              this.type = '';
              this.fftSize = 1024;
            }
            connect(target) {
              window.__audioEvents.push(['connect', this.kind, target && target.kind ? target.kind : 'destination']);
              return target;
            }
            start(time) {
              window.__audioEvents.push(['start', this.kind, this.type, this.frequency.value, time]);
            }
            stop(time) {
              window.__audioEvents.push(['stop', this.kind, time]);
            }
            getByteTimeDomainData(buffer) {
              for (let i = 0; i < buffer.length; i++) {
                buffer[i] = 128 + Math.round(Math.sin(i / 8) * 46);
              }
              window.__audioEvents.push(['scope', buffer.length]);
            }
          }
          class FakeAudioContext {
            constructor() {
              this.state = 'running';
              this.currentTime = 10;
              this.destination = { kind: 'destination' };
              window.__audioEvents.push(['context']);
            }
            resume() {
              this.state = 'running';
              window.__audioEvents.push(['resume']);
              return Promise.resolve();
            }
            createGain() { return new FakeNode('gain'); }
            createBiquadFilter() { return new FakeNode('filter'); }
            createOscillator() { return new FakeNode('oscillator'); }
            createAnalyser() { return new FakeNode('analyser'); }
          }
          window.AudioContext = FakeAudioContext;
          window.webkitAudioContext = FakeAudioContext;
        }
        """)
        self.page.select_option('[data-testid="tone-select"]', "soft_wurli")
        self.page.locator('[data-testid="test-audio"]').click()
        events = self.page.evaluate("() => window.__audioEvents")
        starts = [event for event in events if event[0] == "start"]
        stops = [event for event in events if event[0] == "stop"]
        destination_connections = [event for event in events if event[0] == "connect" and event[2] == "destination"]
        self.assertGreaterEqual(len(starts), 1)
        self.assertGreaterEqual(len(stops), 1)
        self.assertGreaterEqual(len(destination_connections), 1)
        self.assertIn("Audio: playing C4.", self.page.locator('[data-testid="audio-status"]').inner_text())
        self.assertIn("local test tone C4", self.page.locator('[data-testid="diagnostic-log"]').inner_text())
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"scope-readout\"]').textContent.includes('peak')")
        self.assertTrue(self.page.locator('[data-testid="audio-scope"]').is_visible())

    def test_regression_test_tone_uses_loud_local_output(self):
        self.page.evaluate("""
        () => {
          window.__audioEvents = [];
          class FakeParam {
            constructor(name) { this.name = name; this.value = 0; }
            setValueAtTime(value, time) { this.value = value; window.__audioEvents.push(['setValueAtTime', this.name, value, time]); }
            exponentialRampToValueAtTime(value, time) { this.value = value; window.__audioEvents.push(['exponentialRampToValueAtTime', this.name, value, time]); }
          }
          class FakeNode {
            constructor(kind) {
              this.kind = kind;
              this.gain = new FakeParam(kind + '.gain');
              this.frequency = new FakeParam(kind + '.frequency');
              this.Q = { value: 0 };
              this.type = '';
              this.fftSize = 1024;
            }
            connect(target) { window.__audioEvents.push(['connect', this.kind, target && target.kind ? target.kind : 'destination']); return target; }
            disconnect() { window.__audioEvents.push(['disconnect', this.kind]); }
            start(time) { window.__audioEvents.push(['start', this.kind, this.type, this.frequency.value, time]); }
            stop(time) { window.__audioEvents.push(['stop', this.kind, time]); }
            getByteTimeDomainData(buffer) { for (let i = 0; i < buffer.length; i++) buffer[i] = 128; }
          }
          class FakeAudioContext {
            constructor() { this.state = 'running'; this.currentTime = 10; this.destination = { kind: 'destination' }; }
            resume() { return Promise.resolve(); }
            createGain() { return new FakeNode('gain'); }
            createBiquadFilter() { return new FakeNode('filter'); }
            createOscillator() { return new FakeNode('oscillator'); }
            createAnalyser() { return new FakeNode('analyser'); }
          }
          window.AudioContext = FakeAudioContext;
          window.webkitAudioContext = FakeAudioContext;
        }
        """)
        self.page.locator('[data-testid="test-audio"]').click()
        events = self.page.evaluate("() => window.__audioEvents")
        gain_ramps = [event for event in events if event[0] == "exponentialRampToValueAtTime" and event[1] == "gain.gain"]
        master_sets = [event for event in events if event[0] == "setValueAtTime" and event[1] == "gain.gain" and 2.4 <= event[2] <= 2.8]
        self.assertTrue(any(event[2] >= 0.9 for event in gain_ramps), events)
        self.assertTrue(master_sets, events)

    def test_regression_test_tone_bypasses_ssli_and_drives_local_scope(self):
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.__audioEvents = [];
          window.SynthLab = {
            presets: { apply() { window.__ssliCalls.push(['apply']); } },
            audio: {
              getCtx() { window.__ssliCalls.push(['getCtx']); return { state: 'running' }; },
              initEffectChain() { window.__ssliCalls.push(['initEffectChain']); },
              getCurrentInstrument() { return 0; },
              playNoteOnInstrument() { window.__ssliCalls.push(['playNoteOnInstrument']); }
            }
          };
          class FakeParam {
            constructor(name) { this.name = name; this.value = 0; }
            setValueAtTime(value, time) { this.value = value; window.__audioEvents.push(['setValueAtTime', this.name, value, time]); }
            exponentialRampToValueAtTime(value, time) { this.value = value; window.__audioEvents.push(['exponentialRampToValueAtTime', this.name, value, time]); }
          }
          class FakeNode {
            constructor(kind) { this.kind = kind; this.gain = new FakeParam(kind + '.gain'); this.frequency = new FakeParam(kind + '.frequency'); this.Q = { value: 0 }; this.fftSize = 1024; }
            connect(target) { window.__audioEvents.push(['connect', this.kind, target && target.kind ? target.kind : 'destination']); return target; }
            disconnect() {}
            start(time) { window.__audioEvents.push(['start', this.kind, time]); }
            stop(time) { window.__audioEvents.push(['stop', this.kind, time]); }
            getByteTimeDomainData(buffer) { for (let i = 0; i < buffer.length; i++) buffer[i] = 128 + Math.round(Math.sin(i / 7) * 64); }
          }
          class FakeAudioContext {
            constructor() { this.state = 'running'; this.currentTime = 10; this.destination = { kind: 'destination' }; }
            resume() { return Promise.resolve(); }
            createGain() { return new FakeNode('gain'); }
            createBiquadFilter() { return new FakeNode('filter'); }
            createOscillator() { return new FakeNode('oscillator'); }
            createAnalyser() { return new FakeNode('analyser'); }
          }
          window.AudioContext = FakeAudioContext;
          window.webkitAudioContext = FakeAudioContext;
        }
        """)
        self.page.locator('[data-testid="test-audio"]').click()
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"scope-readout\"]').textContent.includes('peak')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        events = self.page.evaluate("() => window.__audioEvents")
        self.assertNotIn(["playNoteOnInstrument"], calls)
        self.assertTrue(any(event[0] == "start" and event[1] == "oscillator" for event in events), events)
        self.assertIn("local test tone", self.page.locator('[data-testid="diagnostic-log"]').inner_text())

    def test_regression_test_tone_scope_draws_visible_waveform(self):
        self.page.evaluate("""
        () => {
          class FakeParam {
            constructor(name) { this.name = name; this.value = 0; }
            setValueAtTime(value) { this.value = value; }
            exponentialRampToValueAtTime(value) { this.value = value; }
          }
          class FakeNode {
            constructor(kind) {
              this.kind = kind;
              this.gain = new FakeParam(kind + '.gain');
              this.frequency = new FakeParam(kind + '.frequency');
              this.Q = { value: 0 };
              this.type = '';
              this.fftSize = 1024;
            }
            connect(target) { return target; }
            disconnect() {}
            start() {}
            stop() {}
            getByteTimeDomainData(buffer) {
              for (let i = 0; i < buffer.length; i++) {
                buffer[i] = 128 + Math.round(Math.sin(i / 5) * 80);
              }
            }
          }
          class FakeAudioContext {
            constructor() { this.state = 'running'; this.currentTime = 10; this.destination = { kind: 'destination' }; }
            resume() { return Promise.resolve(); }
            createGain() { return new FakeNode('gain'); }
            createBiquadFilter() { return new FakeNode('filter'); }
            createOscillator() { return new FakeNode('oscillator'); }
            createAnalyser() { return new FakeNode('analyser'); }
          }
          window.AudioContext = FakeAudioContext;
          window.webkitAudioContext = FakeAudioContext;
        }
        """)
        self.page.locator('[data-testid="test-audio"]').click()
        self.page.wait_for_function("""
        () => {
          const text = document.querySelector('[data-testid="scope-readout"]').textContent;
          const match = text.match(/peak (\\d+)%/);
          return match && Number(match[1]) >= 55;
        }
        """)
        pixel_counts = self.page.evaluate("""
        () => {
          const canvas = document.querySelector('[data-testid="audio-scope"]');
          const data = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
          let green = 0;
          let amber = 0;
          for (let i = 0; i < data.length; i += 4) {
            if (data[i + 1] > 150 && data[i] < 130) green += 1;
            if (data[i] > 180 && data[i + 1] > 120 && data[i + 2] < 120) amber += 1;
          }
          return { green, amber };
        }
        """)
        self.assertGreater(pixel_counts["green"], 120, pixel_counts)
        self.assertGreater(pixel_counts["amber"], 200, pixel_counts)
        scope_height = self.page.locator('[data-testid="audio-scope"]').bounding_box()["height"]
        self.assertGreaterEqual(scope_height, 36)

    def test_regression_real_test_tone_drives_scope_without_mocked_audio_context(self):
        self.open_audio_drawer()
        audio_ctor_info = self.page.evaluate("""() => {
          const ctor = window.AudioContext || window.webkitAudioContext;
          return {
            hasAudioContext: !!ctor,
            isNative: !!ctor && String(ctor).includes('[native code]')
          };
        }""")
        self.assertTrue(audio_ctor_info["hasAudioContext"], audio_ctor_info)
        self.assertTrue(audio_ctor_info["isNative"], audio_ctor_info)

        self.page.locator('[data-testid="test-audio"]').click()
        self.page.wait_for_function("""
        () => {
          const text = document.querySelector('[data-testid="scope-readout"]').textContent;
          const match = text.match(/peak (\\d+)%/);
          return match && Number(match[1]) >= 8;
        }
        """)
        scope = self.page.evaluate("""
        () => {
          const text = document.querySelector('[data-testid="scope-readout"]').textContent;
          const canvas = document.querySelector('[data-testid="audio-scope"]');
          const data = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
          let signalPixels = 0;
          let backgroundPixels = 0;
          for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            if (g > 130 && r < 180) signalPixels += 1;
            if (r < 40 && g < 50 && b < 60) backgroundPixels += 1;
          }
          const match = text.match(/peak (\\d+)%/);
          return {
            text,
            peak: match ? Number(match[1]) : 0,
            signalPixels,
            backgroundPixels,
            width: canvas.width,
            height: canvas.height
          };
        }
        """)
        self.assertGreaterEqual(scope["peak"], 8, scope)
        self.assertGreater(scope["signalPixels"], 50, scope)
        self.assertGreater(scope["backgroundPixels"], 500, scope)

    def test_ssli_sound_and_fx_presets_drive_audio_logs(self):
        self.open_audio_drawer()
        self.assertEqual(self.page.locator('[data-testid="sound-engine-select"] option').count(), 3)
        self.page.select_option('[data-testid="sound-engine-select"]', "subtractive")
        self.page.select_option('[data-testid="sound-category-select"]', "Leads")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Saw Lead")
        self.assertGreater(self.page.locator('[data-testid="fx-category-select"] option').count(), 4)
        self.page.select_option('[data-testid="fx-category-select"]', "Performance / Live")
        self.page.select_option('[data-testid="fx-preset-select"]', "lead-solo")
        self.page.locator('[data-testid="play-step"]').click()
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("preset=subtractive::Saw Lead", log)
        self.assertIn("fx=lead-solo", log)

    def test_regression_preset_changes_audio_graph_not_just_label(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: {
              apply(preset, inst) {
                window.__ssliCalls.push(['apply', preset.engine, preset.name, JSON.stringify(preset.settings || {}), inst]);
              }
            },
            audio: {
              getCtx() { window.__ssliCalls.push(['getCtx']); return {}; },
              initEffectChain() { window.__ssliCalls.push(['initEffectChain']); },
              getCurrentInstrument() { return 0; },
              playNoteOnInstrument(midi, dur, inst, vel) {
                window.__ssliCalls.push(['play', midi, dur, inst, vel]);
              }
            }
          };
        }
        """)
        self.page.select_option('[data-testid="sound-engine-select"]', "fm")
        self.page.select_option('[data-testid="sound-category-select"]', "Bass")
        self.page.select_option('[data-testid="sound-preset-select"]', label="BASS 1")
        self.page.locator('[data-testid="play-step"]').click()
        fm_signature = self.page.evaluate("() => window.__ssliCalls.filter((event) => event[0] === 'apply').at(-1)")
        self.page.locator('[data-testid="show-all-engines"]').check()
        self.page.select_option('[data-testid="sound-engine-select"]', "wavetable-synth")
        self.page.select_option('[data-testid="sound-category-select"]', "Pads")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Warm Analog Pad")
        self.page.locator('[data-testid="play-step"]').click()
        wavetable_signature = self.page.evaluate("() => window.__ssliCalls.filter((event) => event[0] === 'apply').at(-1)")
        plays = self.page.evaluate("() => window.__ssliCalls.filter((event) => event[0] === 'play').length")
        self.assertEqual(fm_signature[1], "fm")
        self.assertEqual(wavetable_signature[1], "wavetable")
        self.assertNotEqual(fm_signature, wavetable_signature)
        self.assertGreaterEqual(plays, 2)

    def test_regression_ssli_runtime_preset_changes_played_instrument(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const instruments = [{ type: 'subtractive', settings: { marker: 'default-sound', filter: { freq: 777 } } }];
          const runtimeBass = {
            __runtimePreset: true,
            name: 'BASS 1',
            category: 'Bass',
            engine: 'fm',
            settings: { marker: 'runtime-fm-bass', fm: { algorithm: 6 }, filter: { freq: 612 } }
          };
          window.SynthLab = {
            presets: {
              getEngines() { return ['Subtractive', 'FM']; },
              getCategoriesForEngine(engine) {
                window.__ssliCalls.push(['getCategoriesForEngine', engine]);
                return engine === 'FM' ? ['Bass'] : ['Keys'];
              },
              getPresetsForEngineCategory(engine, category) {
                window.__ssliCalls.push(['getPresetsForEngineCategory', engine, category]);
                return engine === 'FM' && category === 'Bass' ? [runtimeBass] : [];
              },
              engineNameToType(engine) {
                window.__ssliCalls.push(['engineNameToType', engine]);
                return engine === 'FM' ? 'fm' : 'subtractive';
              },
              apply(preset, inst) {
                window.__ssliCalls.push(['apply', preset.engine, preset.name, !!preset.__runtimePreset, inst]);
                if (preset.__runtimePreset) {
                  instruments[inst || 0].type = preset.engine;
                  instruments[inst || 0].settings = JSON.parse(JSON.stringify(preset.settings));
                }
              }
            },
            state: { notify(kind) { window.__ssliCalls.push(['notify', kind]); } },
            audio: {
              getCtx() { return { state: 'running', resume() { window.__ssliCalls.push(['resume']); } }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return instruments; },
              loadInstrumentSettings(inst) { window.__ssliCalls.push(['loadInstrumentSettings', inst, instruments[inst].settings.marker]); },
              refreshFilter() { window.__ssliCalls.push(['refreshFilter']); },
              freqToSlider(value) { window.__ssliCalls.push(['freqToSlider', value]); return 'slider:' + value; },
              qToSlider(value) { window.__ssliCalls.push(['qToSlider', value]); return 'q:' + value; },
              playNoteOnInstrument(midi, dur, inst, vel) {
                const current = instruments[inst || 0];
                window.__ssliCalls.push(['playSnapshot', current.type, current.settings.marker, current.settings.filter && current.settings.filter.freq, vel]);
              }
            }
          };
          document.getElementById('ssliEngineFrame').dispatchEvent(new Event('load'));
        }
        """)
        self.page.select_option('[data-testid="sound-engine-select"]', "FM")
        self.page.select_option('[data-testid="sound-category-select"]', "Bass")
        self.page.select_option('[data-testid="sound-preset-select"]', label="BASS 1")
        self.page.locator('[data-testid="play-step"]').click()
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["getPresetsForEngineCategory", "FM", "Bass"], calls)
        self.assertIn(["apply", "fm", "BASS 1", True, 0], calls)
        self.assertIn(["notify", "preset"], calls)
        self.assertIn(["playSnapshot", "fm", "runtime-fm-bass", 612, 127], calls)
        self.assertNotIn(["freqToSlider", 2200], calls)

    def test_regression_preset_signature_check_intones_distinct_real_engines(self):
        result = subprocess.run(
            [
                "python",
                "tools/preset_signature_check.py",
                "--no-build",
                "--output",
                "tmp_preset_signature_check/unittest_real_engines.json",
                "--sample-ms",
                "900",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_regression_preset_signature_check_intones_physical_koto_through_midi(self):
        output = ROOT / "tmp_preset_signature_check/unittest_midi_koto.json"
        result = subprocess.run(
            [
                "python",
                "tools/preset_signature_check.py",
                "--no-build",
                "--trigger",
                "midi",
                "--case",
                "Physical/Plucked/Koto/physical",
                "--output",
                str(output.relative_to(ROOT)),
                "--sample-ms",
                "900",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(output.read_text(encoding="utf-8"))
        koto = payload["results"][0]
        self.assertEqual(koto["instrumentType"], "physical", koto)
        self.assertEqual(koto["engineSettings"].get("model"), "pluck", koto)
        self.assertGreaterEqual(koto["peak"], 0.02, koto)
        self.assertGreaterEqual(koto["rms"], 0.01, koto)
        self.assertGreaterEqual(koto["spectrumPeak"], 0.4, koto)

    def test_regression_preset_sweep_runs_mature_engine_category_continuous_poly_aftertouch_audio(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_mature_poly"
        result = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--mature-engines-only",
                "--one-per-category",
                "--trigger",
                "continuous-poly-pressure-midi",
                "--audio-sample-ms",
                "900",
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=300,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        results = payload["results"]
        engine_categories = {(row["engine"], row["categoryLabel"]) for row in results}
        engines = {row["engine"].lower() for row in results}
        self.assertEqual(engines, {"fm", "physical", "subtractive"}, payload)
        self.assertEqual(payload["summary"]["failed"], 0, payload)
        self.assertEqual(payload["summary"]["sweptPresetCount"], len(engine_categories), payload)
        self.assertGreaterEqual(payload["summary"]["sweptPresetCount"], 6, payload)
        for row in results:
            self.assertEqual(row["trigger"], "continuous-poly-pressure-midi", row)
            self.assertTrue(row["audioSignatureAvailable"], row)
            self.assertGreater(float(row["audioRms"]), 0.003, row)
            self.assertLessEqual(float(row["audioClipRatio"]), 0.03, row)
            self.assertGreaterEqual(int(row["audioSignature"]["polyAftertouchEvents"]), 12, row)
            self.assertEqual(int(row["audioSignature"]["channelPressureEvents"]), 0, row)

    def test_regression_preset_sweep_runs_mature_engine_category_200_note_voice_stress_audio(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_mature_voice_stress"
        result = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--mature-engines-only",
                "--one-per-category",
                "--trigger",
                "voice-stress-midi",
                "--audio-sample-ms",
                "1400",
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=600,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        results = payload["results"]
        engines = {row["engine"].lower() for row in results}
        self.assertEqual(engines, {"fm", "physical", "subtractive"}, payload)
        self.assertEqual(payload["summary"]["failed"], 0, payload)
        self.assertGreaterEqual(payload["summary"]["sweptPresetCount"], 6, payload)
        for row in results:
            signature = row["audioSignature"]
            self.assertEqual(row["trigger"], "voice-stress-midi", row)
            self.assertTrue(row["audioSignatureAvailable"], row)
            self.assertEqual(int(signature["noteOns"]), 200, row)
            self.assertEqual(int(signature["noteOffs"]), 200, row)
            self.assertGreaterEqual(int(signature["observedMaxHeld"]), 6, row)
            self.assertGreaterEqual(int(signature["observedMaxLocalVoices"]), 6, row)
            self.assertEqual(int(signature["voiceLossCount"]), 0, row)
            self.assertGreaterEqual(int(signature["polyAftertouchSent"]), 200, row)
            self.assertEqual(int(signature["channelPressureSent"]), 0, row)
            self.assertGreater(float(row["audioRms"]), 0.003, row)
            self.assertLessEqual(float(row["audioClipRatio"]), 0.03, row)

    def test_regression_first_noise_industrial_preset_survives_six_note_poly_pressure_audio(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_noise_industrial"
        result = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--engine",
                "Subtractive",
                "--category",
                "Noise/Industrial",
                "--preset-contains",
                "White Noise Sweep",
                "--trigger",
                "six-note-midi",
                "--audio-sample-ms",
                "900",
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["summary"]["failed"], 0, payload)
        row = payload["results"][0]
        self.assertEqual(row["presetLabel"], "White Noise Sweep", row)
        self.assertGreater(float(row["audioRms"]), 0.003, row)
        self.assertLessEqual(float(row["audioClipRatio"]), 0.03, row)

    def test_regression_fm_dx_rhodes_uat_audio_acceptance(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_fm_dx_rhodes_uat"
        result = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--engine",
                "FM",
                "--category",
                "Keys",
                "--preset-contains",
                "DX RHODES",
                "--trigger",
                "six-note-midi",
                "--audio-sample-ms",
                "1200",
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["results"]), 1, payload)
        row = payload["results"][0]
        self.assertEqual(row["presetLabel"], "DX RHODES", row)
        self.assertEqual(row["instrumentType"], "fm", row)
        self.assertIn("SSLI preset corrected engine=fm preset=DX RHODES", row["audioSignature"]["diagnosticLog"])
        self.assertEqual(
            result.returncode,
            0,
            "DX RHODES UAT failure must be machine-detectable before user retest. "
            "User reported: very noisy/poppy, very bell-like. "
            f"row={json.dumps(row, indent=2)}\nstdout={result.stdout}\nstderr={result.stderr}",
        )
        self.assertEqual(payload["summary"]["failed"], 0, payload)
        self.assertGreater(float(row["audioRms"]), 0.003, row)
        self.assertLessEqual(float(row["audioRms"]), 0.35, row)
        self.assertLessEqual(float(row["audioP95Peak"]), 0.75, row)
        self.assertLessEqual(float(row["audioClipRatio"]), 0.03, row)
        signature = row["audioSignature"]
        self.assertLessEqual(float(signature["peakToRms"]), 5.0, row)
        reference_cases = [
            ("Keys", "FM::DX RHODES", "tests/fixtures/dx7/vrc110a.syx", "VicRhodes\\"),
            ("Keys", "FM::E.PIANO 1", "tests/fixtures/dx7/rom1a.syx", "E.PIANO 1"),
            ("Keys", "FM::TINE PIANO", "tests/fixtures/dx7/vrc108a.syx", "FullTines"),
            ("Keys", "FM::WURLITZER FM", "tests/fixtures/dx7/vrc110a.syx", "WurliChrs\\"),
        ]
        reference_payloads = []
        for category, preset, bank, voice in reference_cases:
            reference_output = ROOT / "tmp_fm_reference_compare_unittest_dx_rhodes" / (preset.replace("::", "_").replace(".", "_") + ".json")
            reference = subprocess.run(
                [
                    "python",
                    "tools/fm_reference_compare.py",
                    "--no-build",
                    "--category",
                    category,
                    "--preset",
                    preset,
                    "--reference-bank",
                    bank,
                    "--reference-voice",
                    voice,
                    "--max-centroid-ratio-delta",
                    "1.0",
                    "--output",
                    str(reference_output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=120,
            )
            reference_payload = json.loads(reference_output.read_text(encoding="utf-8"))
            reference_payloads.append(reference_payload)
            self.assertEqual(
                reference.returncode,
                0,
                f"{preset} must match the Yamaha/Dexed reference, not only generic spectral thresholds. "
                f"payload={json.dumps(reference_payload, indent=2)}"
                f"\nstdout={reference.stdout}\nstderr={reference.stderr}",
            )
            self.assertEqual(reference_payload["status"], "pass", reference_payload)

        diversity_output_dir = ROOT / "tmp_preset_sweep_unittest_fm_key_diversity"
        diversity = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--engine",
                "FM",
                "--category",
                "Keys",
                "--preset-list-file",
                "tests/fixtures/ssli_fm_key_timbre_acceptance_list.json",
                "--trigger",
                "six-note-midi",
                "--audio-sample-ms",
                "1200",
                "--output-dir",
                str(diversity_output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        self.assertEqual(diversity.returncode, 0, diversity.stdout + diversity.stderr)
        diversity_payload = json.loads((diversity_output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        rows_by_label = {item["presetLabel"]: item for item in diversity_payload["results"]}
        exhibit_centroids = [
            float(rows_by_label[label]["audioSignature"]["spectrumCentroidHz"])
            for label in ("DX RHODES", "TINE PIANO", "WURLITZER FM")
        ]
        self.assertGreaterEqual(
            max(exhibit_centroids) - min(exhibit_centroids),
            400,
            {
                "message": "User reported FM keys all sound very similar; exhibit must preserve source-truth timbre spread.",
                "exhibitCentroids": exhibit_centroids,
                "rows": {label: rows_by_label[label] for label in ("DX RHODES", "TINE PIANO", "WURLITZER FM")},
            },
        )

    def test_regression_fm_dx_rhodes_normal_pressure_is_playable(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_fm_dx_rhodes_normal_pressure"
        result = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--engine",
                "FM",
                "--category",
                "Keys",
                "--preset-contains",
                "DX RHODES",
                "--trigger",
                "single-midi",
                "--normalization-midi",
                "48",
                "--normalization-pressure",
                "48",
                "--audio-sample-ms",
                "1200",
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        row = payload["results"][0]
        self.assertEqual(result.returncode, 0, f"row={json.dumps(row, indent=2)}\nstdout={result.stdout}\nstderr={result.stderr}")
        self.assertEqual(row["presetLabel"], "DX RHODES", row)
        self.assertEqual(row["instrumentType"], "fm", row)
        self.assertGreaterEqual(float(row["audioRms"]), 0.055, row)
        self.assertGreaterEqual(float(row["audioPeak"]), 0.120, row)
        self.assertLessEqual(float(row["audioClipRatio"]), 0.01, row)

    def test_regression_uat_fm_spot_presets_do_not_collapse_to_same_timbre(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_fm_uat_spot_timbre_diversity"
        preset_list = ROOT / "tmp_fm_uat_spot_timbre_list.json"
        preset_list.write_text(json.dumps([
            {"engine": "FM", "category": "Keys", "preset": "FM::CELESTA", "presetLabel": "CELESTA", "status": "fail"},
            {"engine": "FM", "category": "Keys", "preset": "FM::DX RHODES", "presetLabel": "DX RHODES", "status": "fail"},
            {"engine": "FM", "category": "Brass", "preset": "FM::BRASS 1", "presetLabel": "BRASS 1", "status": "fail"},
            {"engine": "FM", "category": "Bass", "preset": "FM::BASS 1", "presetLabel": "BASS 1", "status": "fail"},
        ]), encoding="utf-8")
        result = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--engine",
                "FM",
                "--preset-list-file",
                str(preset_list),
                "--trigger",
                "six-note-midi",
                "--audio-sample-ms",
                "1200",
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        rows_by_label = {item["presetLabel"]: item for item in payload["results"]}
        labels = ("CELESTA", "DX RHODES", "BRASS 1", "BASS 1")
        spectrum_hashes = {rows_by_label[label]["audioSpectrumHash"] for label in labels}
        waveform_hashes = {rows_by_label[label]["audioWaveformHash"] for label in labels}
        centroids = [float(rows_by_label[label]["audioSignature"]["spectrumCentroidHz"]) for label in labels]
        self.assertEqual(len(spectrum_hashes), len(labels), rows_by_label)
        self.assertEqual(len(waveform_hashes), len(labels), rows_by_label)
        self.assertGreaterEqual(max(centroids) - min(centroids), 900, {"centroids": centroids, "rows": rows_by_label})

    def test_regression_uat_quiet_spot_presets_clear_single_note_floor(self):
        cases = [
            ("Subtractive", "Celesta", "Celesta", 0.008, 0.035),
            ("Subtractive", "Synth Brass", "Synth Brass Section", 0.025, 0.080),
            ("Subtractive", "Saw Lead", "Saw Lead", 0.024, 0.060),
            ("FM", "CELESTA", "CELESTA", 0.010, 0.025),
            ("FM", "BRASS 1", "BRASS 1", 0.010, 0.025),
            ("FM", "BASS 1", "BASS 1", 0.020, 0.035),
            ("Physical", "Nylon Guitar", "Nylon Guitar", 0.006, 0.030),
        ]
        for engine, contains, label, min_rms, min_peak in cases:
            with self.subTest(engine=engine, preset=label):
                output_dir = ROOT / f"tmp_preset_sweep_unittest_quiet_{engine}_{contains}".replace(" ", "_").replace(".", "_")
                result = subprocess.run(
                    [
                        "python",
                        "tools/preset_sweep.py",
                        "--no-build",
                        "--engine",
                        engine,
                        "--preset-contains",
                        contains,
                        "--trigger",
                        "single-midi",
                        "--normalization-midi",
                        "48",
                        "--audio-sample-ms",
                        "1400",
                        "--output-dir",
                        str(output_dir),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    timeout=120,
                )
                payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
                row = next(item for item in payload["results"] if item["presetLabel"] == label)
                self.assertEqual(result.returncode, 0, f"row={json.dumps(row, indent=2)}\nstdout={result.stdout}\nstderr={result.stderr}")
                if engine == "Physical" and label == "Nylon Guitar":
                    physical_settings = row["audioSignature"]["physicalSettings"]
                    self.assertEqual(physical_settings["model"], "pluck", row)
                    self.assertEqual(physical_settings["excitation"], "pick", row)
                    self.assertEqual(physical_settings["bodySize"], 60, row)
                    self.assertGreaterEqual(float(row["audioSignature"]["spectrumCentroidHz"]), 700, row)
                    self.assertGreaterEqual(float(row["audioSignature"]["spectrumHighRatio"]), 0.01, row)
                self.assertGreaterEqual(float(row["audioRms"]), min_rms, row)
                self.assertGreaterEqual(float(row["audioPeak"]), min_peak, row)
                self.assertLessEqual(float(row["audioMaxSampleStep"]), 0.12, row)
                self.assertLessEqual(float(row["audioP95SampleStep"]), 0.08, row)
                self.assertLessEqual(float(row["audioClipRatio"]), 0.01, row)

    def test_regression_physical_marimba_c3_is_balanced_against_c4(self):
        rows = {}
        for midi, note in ((48, "C3"), (60, "C4")):
            output_dir = ROOT / f"tmp_preset_sweep_unittest_marimba_{note.lower()}"
            result = subprocess.run(
                [
                    "python",
                    "tools/preset_sweep.py",
                    "--no-build",
                    "--engine",
                    "Physical",
                    "--preset-contains",
                    "Marimba",
                    "--trigger",
                    "single-midi",
                    "--normalization-midi",
                    str(midi),
                    "--audio-sample-ms",
                    "1400",
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=120,
            )
            payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
            row = next(item for item in payload["results"] if item["presetLabel"] == "Marimba")
            self.assertEqual(result.returncode, 0, f"{note} row={json.dumps(row, indent=2)}\nstdout={result.stdout}\nstderr={result.stderr}")
            rows[note] = row
        self.assertLessEqual(float(rows["C3"]["audioP95Peak"]), 0.20, rows)
        self.assertLessEqual(float(rows["C3"]["audioPeak"]), 0.30, rows)
        self.assertLessEqual(float(rows["C3"]["audioP95Peak"]) / max(0.001, float(rows["C4"]["audioP95Peak"])), 3.5, rows)
        self.assertLessEqual(float(rows["C3"]["audioClipRatio"]), 0.01, rows)

    def test_regression_uat_spot_presets_have_medium_velocity_loudness(self):
        cases = [
            ("Subtractive", "Celesta", "Celesta", 0.008, 0.028),
            ("Subtractive", "Synth Brass", "Synth Brass Section", 0.025, 0.080),
            ("Subtractive", "Saw Lead", "Saw Lead", 0.040, 0.100),
            ("FM", "CELESTA", "CELESTA", 0.040, 0.130),
            ("FM", "DX RHODES", "DX RHODES", 0.055, 0.120),
            ("FM", "BRASS 1", "BRASS 1", 0.120, 0.240),
            ("FM", "BASS 1", "BASS 1", 0.055, 0.100),
            ("Physical", "Nylon Guitar", "Nylon Guitar", 0.0095, 0.055),
        ]
        for engine, contains, label, min_rms, min_peak in cases:
            with self.subTest(engine=engine, preset=label):
                output_dir = ROOT / f"tmp_preset_sweep_unittest_medium_velocity_{engine}_{contains}".replace(" ", "_").replace(".", "_")
                result = subprocess.run(
                    [
                        "python",
                        "tools/preset_sweep.py",
                        "--no-build",
                        "--engine",
                        engine,
                        "--preset-contains",
                        contains,
                        "--trigger",
                        "single-midi",
                        "--normalization-midi",
                        "48",
                        "--normalization-pressure",
                        "64",
                        "--audio-sample-ms",
                        "1200",
                        "--output-dir",
                        str(output_dir),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    timeout=120,
                )
                payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
                row = next(item for item in payload["results"] if item["presetLabel"] == label)
                self.assertEqual(result.returncode, 0, f"row={json.dumps(row, indent=2)}\nstdout={result.stdout}\nstderr={result.stderr}")
                if engine == "Physical" and label == "Nylon Guitar":
                    physical_settings = row["audioSignature"]["physicalSettings"]
                    self.assertEqual(physical_settings["model"], "pluck", row)
                    self.assertEqual(physical_settings["excitation"], "pick", row)
                    self.assertEqual(physical_settings["bodySize"], 60, row)
                    self.assertGreaterEqual(float(row["audioSignature"]["spectrumCentroidHz"]), 700, row)
                    self.assertGreaterEqual(float(row["audioSignature"]["spectrumHighRatio"]), 0.01, row)
                self.assertGreaterEqual(float(row["audioRms"]), min_rms, row)
                self.assertGreaterEqual(float(row["audioPeak"]), min_peak, row)
                max_sample_step = 0.30 if engine == "FM" and label == "BRASS 1" else 0.12
                self.assertLessEqual(float(row["audioMaxSampleStep"]), max_sample_step, row)
                self.assertLessEqual(float(row["audioP95SampleStep"]), 0.08, row)
                self.assertLessEqual(float(row["audioClipRatio"]), 0.01, row)

    def test_regression_physical_nylon_guitar_does_not_ring_like_sustained_pad(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_physical_nylon_long_release"
        result = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--engine",
                "Physical",
                "--preset-contains",
                "Nylon Guitar",
                "--trigger",
                "single-midi",
                "--normalization-midi",
                "48",
                "--normalization-pressure",
                "64",
                "--audio-sample-ms",
                "2600",
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        row = next(item for item in payload["results"] if item["presetLabel"] == "Nylon Guitar")
        self.assertEqual(result.returncode, 0, f"row={json.dumps(row, indent=2)}\nstdout={result.stdout}\nstderr={result.stderr}")
        self.assertLessEqual(float(row["audioRms"]), 0.015, row)
        self.assertLessEqual(float(row["audioTailRms"]), 0.003, row)
        self.assertLessEqual(float(row["audioClipRatio"]), 0.01, row)

    def test_regression_sound_selectors_use_live_ssli_preset_api_when_available(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: {
              getEngines() { window.__ssliCalls.push(['getEngines']); return ['CustomEngine']; },
              getCategoriesForEngine(engine) { window.__ssliCalls.push(['getCategoriesForEngine', engine]); return ['CustomCat']; },
              getPresetsForEngineCategory(engine, category) {
                window.__ssliCalls.push(['getPresetsForEngineCategory', engine, category]);
                return [{ name: 'CustomPreset', category: 'CustomCat', engine: 'subtractive', settings: { marker: 'live-api-only' } }];
              },
              engineNameToType(engine) { window.__ssliCalls.push(['engineNameToType', engine]); return 'subtractive'; },
              apply() {}
            },
            audio: {
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ settings: {} }]; }
            }
          };
          document.getElementById('ssliEngineFrame').dispatchEvent(new Event('load'));
        }
        """)
        engines = self.page.locator('[data-testid="sound-engine-select"] option').evaluate_all("(opts) => opts.map((opt) => opt.value)")
        categories = self.page.locator('[data-testid="sound-category-select"] option').evaluate_all("(opts) => opts.map((opt) => opt.value)")
        presets = self.page.locator('[data-testid="sound-preset-select"] option').evaluate_all("(opts) => opts.map((opt) => opt.textContent.trim())")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual(engines, ["CustomEngine"])
        self.assertEqual(categories, ["CustomCat"])
        self.assertEqual(presets, ["CustomPreset"])
        self.assertIn(["getEngines"], calls)
        self.assertIn(["getCategoriesForEngine", "CustomEngine"], calls)
        self.assertIn(["getPresetsForEngineCategory", "CustomEngine", "CustomCat"], calls)

    def test_regression_sound_engine_dropdown_defaults_to_mature_engines_with_show_all_opt_in(self):
        self.open_audio_drawer()
        default_engines = self.page.locator('[data-testid="sound-engine-select"] option').evaluate_all("(opts) => opts.map((opt) => opt.value)")
        self.assertFalse(self.page.locator('[data-testid="show-all-engines"]').is_checked())
        self.assertEqual(default_engines, ["fm", "physical", "subtractive"])
        self.assertNotIn("wavetable-synth", default_engines)
        self.page.locator('[data-testid="show-all-engines"]').check()
        all_engines = self.page.locator('[data-testid="sound-engine-select"] option').evaluate_all("(opts) => opts.map((opt) => opt.value)")
        self.assertIn("wavetable-synth", all_engines)
        self.assertGreater(len(all_engines), len(default_engines))

    def test_regression_subtractive_runtime_preset_filter_cutoff_is_normalized(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const instruments = [{ type: 'subtractive', settings: { marker: 'default-sound', filter: { freq: 777 } } }];
          const badRuntimePreset = {
            __runtimePreset: true,
            name: 'First Light',
            category: 'Ambient',
            engine: 'subtractive',
            settings: { marker: 'normalized-subtractive', filter: { enabled: true, type: 'lowpass', freq: 2800, q: 8, keyTrack: 50 } }
          };
          window.SynthLab = {
            presets: {
              getEngines() { return ['Subtractive']; },
              getCategoriesForEngine() { return ['Ambient']; },
              getPresetsForEngineCategory(engine, category) {
                window.__ssliCalls.push(['getPresetsForEngineCategory', engine, category]);
                return [badRuntimePreset];
              },
              engineNameToType(engine) {
                window.__ssliCalls.push(['engineNameToType', engine]);
                return 'subtractive';
              },
              apply(preset, inst) {
                window.__ssliCalls.push(['applyFilterFreq', preset.name, preset.settings.filter.freq]);
                instruments[inst || 0].type = preset.engine;
                instruments[inst || 0].settings = JSON.parse(JSON.stringify(preset.settings));
              }
            },
            state: { notify(kind) { window.__ssliCalls.push(['notify', kind]); } },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return instruments; },
              freqToSlider(value) { window.__ssliCalls.push(['freqToSlider', value]); return 715; },
              playNoteOnInstrument(midi, dur, inst, vel) {
                const current = instruments[inst || 0];
                window.__ssliCalls.push(['playFilterFreq', current.settings.filter.freq, vel]);
              }
            }
          };
        }
        """)
        self.page.select_option('[data-testid="sound-engine-select"]', "subtractive")
        self.page.select_option('[data-testid="sound-category-select"]', "Ambient")
        self.page.select_option('[data-testid="sound-preset-select"]', label="First Light")
        self.page.locator('[data-testid="play-step"]').click()
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["freqToSlider", 2800], calls)
        self.assertIn(["applyFilterFreq", "First Light", 715], calls)
        self.assertIn(["playFilterFreq", 715, 127], calls)
        self.assertNotIn(["applyFilterFreq", "First Light", 2800], calls)

    def test_regression_physical_koto_applies_model_settings_without_preview_expression_override(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const instruments = [{ type: 'subtractive', settings: { physicalSettings: {} } }];
          const koto = {
            name: 'Koto',
            category: 'Plucked',
            engine: 'physical',
            settings: {
              model: 'pluck',
              damping: 35,
              brightness: 75,
              excitation: 'pick',
              bodySize: 50,
              decayTime: 60
            }
          };
          window.SynthLab = {
            presets: {
              getEngines() { return ['Physical']; },
              getCategoriesForEngine(engine) { return ['Plucked']; },
              getPresetsForEngineCategory(engine, category) {
                window.__ssliCalls.push(['getPresetsForEngineCategory', engine, category]);
                return [koto];
              },
              engineNameToType(engine) { return 'physical'; },
              apply(preset, inst) {
                window.__ssliCalls.push(['apply', preset.engine, preset.name]);
                window.SynthLab.audio.setInstrumentType(inst || 0, 'physical');
                window.SynthLab.audio.setPhysicalSettings(inst || 0, preset.settings);
              }
            },
            state: { notify(kind) { window.__ssliCalls.push(['notify', kind]); } },
            physical: {
              setSettings(inst, settings) { window.__ssliCalls.push(['physical.setSettings', inst, settings.model, settings.damping, settings.brightness, settings.excitation, settings.bodySize, settings.decayTime]); },
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst, instruments[inst].settings.physicalSettings.model, instruments[inst].settings.physicalSettings.excitation]); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); },
              init() { window.__ssliCalls.push(['physical.init']); }
            },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return instruments; },
              setInstrumentType(inst, type) { instruments[inst].type = type; window.__ssliCalls.push(['setInstrumentType', inst, type]); },
              setPhysicalSettings(inst, settings) {
                instruments[inst].settings.physicalSettings = Object.assign({}, instruments[inst].settings.physicalSettings || {}, settings);
                window.__ssliCalls.push(['setPhysicalSettings', inst, settings.model, settings.damping, settings.brightness, settings.excitation, settings.bodySize, settings.decayTime]);
                window.SynthLab.physical.setSettings(inst, instruments[inst].settings.physicalSettings);
              },
              loadInstrumentSettings(inst) { window.__ssliCalls.push(['loadInstrumentSettings', inst]); },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained']); },
              setExpression(cutoff, gain) { window.__ssliCalls.push(['setExpression', cutoff, gain]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); },
              playNoteOnInstrument(midi, dur, inst, vel) {
                const current = instruments[inst || 0];
                if (current.type === 'physical') {
                  window.SynthLab.physical.noteOn(midi, vel, inst || 0);
                } else {
                  window.__ssliCalls.push(['wrongEnginePlay', current.type]);
                }
              }
            }
          };
          document.getElementById('ssliEngineFrame').dispatchEvent(new Event('load'));
        }
        """)
        self.page.select_option('[data-testid="sound-engine-select"]', "Physical")
        self.page.select_option('[data-testid="sound-category-select"]', "Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Koto")
        self.page.locator('[data-testid="play-step"]').click()
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["setPhysicalSettings", 0, "pluck", 35, 75, "pick", 50, 60], calls)
        self.assertIn(["physical.setSettings", 0, "pluck", 35, 75, "pick", 50, 60], calls)
        self.assertTrue(any(call[:3] == ["physical.noteOn", 48, 127] and call[3:] == [0, "pluck", "pick"] for call in calls), calls)
        self.assertNotIn(["setExpression", 10000, 1.3], calls)
        self.assertFalse(any(call[0] == "wrongEnginePlay" for call in calls), calls)

    def test_regression_midi_reapplies_preset_when_live_ssli_engine_does_not_match_cache(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const instruments = [{ type: 'subtractive', settings: { volume: 100, filter: {}, effects: {}, physicalSettings: {} } }];
          const koto = {
            __runtimePreset: true,
            name: 'Koto',
            category: 'Plucked',
            engine: 'physical',
            settings: {
              physicalSettings: { model: 'pluck', damping: 35, brightness: 75, excitation: 'pick' },
              filter: {},
              effects: {},
              volume: 100
            }
          };
          window.SynthLab = {
            presets: {
              getEngines() { return ['Physical']; },
              getCategoriesForEngine() { return ['Plucked']; },
              getPresetsForEngineCategory() { return [koto]; },
              engineNameToType() { return 'physical'; },
              apply(preset, inst) {
                window.__ssliCalls.push(['apply', preset.engine, preset.name, instruments[inst || 0].type]);
                instruments[inst || 0].type = preset.engine;
                instruments[inst || 0].settings = JSON.parse(JSON.stringify(preset.settings));
              }
            },
            state: { notify(kind) { window.__ssliCalls.push(['notify', kind]); } },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return instruments; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained']); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity, instruments[0].type, instruments[0].settings.physicalSettings.model]); },
              stopSustainedNote() {},
              setExpression() {},
              clearExpression() {}
            }
          };
          document.getElementById('ssliEngineFrame').dispatchEvent(new Event('load'));
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
          window.__forceWrongLiveEngine = () => {
            instruments[0].type = 'subtractive';
            instruments[0].settings = { volume: 100, filter: {}, effects: {}, physicalSettings: {} };
          };
        }
        """)
        self.page.select_option('[data-testid="sound-engine-select"]', "Physical")
        self.page.select_option('[data-testid="sound-category-select"]', "Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Koto")
        self.page.evaluate("() => window.__forceWrongLiveEngine()")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x92, 48, 64] })")
        self.page.wait_for_function("() => window.__ssliCalls.some(call => call[0] === 'startSustainedNote')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertGreaterEqual(len([call for call in calls if call[0] == "apply" and call[1] == "physical" and call[2] == "Koto"]), 2, calls)
        self.assertIn(["startSustainedNote", 48, 69, "physical", "pluck"], calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("expected=physical", log)
        self.assertIn("MISMATCH", log)

    def test_regression_physical_midi_uses_tracked_ssli_sustained_voice_with_velocity(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const instruments = [{ type: 'physical', settings: { volume: 100, physicalSettings: { model: 'bow' }, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            physical: {
              noteOn(midi, velocity, inst) {
                window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst]);
                activeOscs.set(midi, { physical: true });
              },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); activeOscs.delete(midi); },
              allNotesOff(inst) { window.__ssliCalls.push(['physical.allNotesOff', inst]); activeOscs.clear(); }
            },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'physical'; },
              getInstruments() { return instruments; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) {
                window.__ssliCalls.push(['startSustainedNote', midi, velocity]);
                window.SynthLab.physical.noteOn(midi, velocity, 0);
              },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); window.SynthLab.physical.noteOff(midi, 0); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x92, 48, 96] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["startSustainedNote", 48, 96], calls)
        self.assertIn(["physical.noteOn", 48, 96, 0], calls)
        self.assertNotIn(["physical.noteOn", 48, 180, 0], calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("MIDI voices after-start C3 held=1 local=1 ssli=1", log)
        self.assertIn("activeOsc=1", log)

    def test_regression_physical_midi_idle_calls_physical_all_notes_off(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const instruments = [{ type: 'physical', settings: { volume: 100, physicalSettings: { model: 'bow' }, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            physical: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst]); activeOscs.set(midi, { physical: true }); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); activeOscs.delete(midi); },
              updateNotePressure(midi, pressure, inst) { window.__ssliCalls.push(['physical.updateNotePressure', midi, pressure, inst]); },
              allNotesOff(inst) { window.__ssliCalls.push(['physical.allNotesOff', inst]); activeOscs.clear(); }
            },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'physical'; },
              getInstruments() { return instruments; },
              getVoicePoolStats() { return { totalAllocated: 80, peakUsage: 1, steals: 0, currentlyActive: 0, available: 80 }; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); window.SynthLab.physical.noteOn(midi, velocity, 0); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); window.SynthLab.physical.noteOff(midi, 0); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x92, 48, 96] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x82, 48, 0] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["physical.allNotesOff", 0], calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI engine all-notes-off after MIDI idle inst=0", log)
        self.assertNotIn("activeOsc/pool mismatch", log)

    def test_regression_physical_midi_pressure_does_not_call_global_expression(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const instruments = [{ type: 'physical', settings: { volume: 100, physicalSettings: { model: 'bow' }, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            physical: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst]); activeOscs.set(midi, { physical: true }); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); activeOscs.delete(midi); },
              updateNotePressure(midi, pressure, inst) { window.__ssliCalls.push(['physical.updateNotePressure', midi, pressure, inst]); },
              allNotesOff(inst) { window.__ssliCalls.push(['physical.allNotesOff', inst]); activeOscs.clear(); }
            },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'physical'; },
              getInstruments() { return instruments; },
              getVoicePoolStats() { return { totalAllocated: 80, peakUsage: 1, steals: 0, currentlyActive: 0, available: 80 }; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); window.SynthLab.physical.noteOn(midi, velocity, 0); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); window.SynthLab.physical.noteOff(midi, 0); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x92, 48, 54] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xD2, 106] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xD2, 0] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["startSustainedNote", 48, 81], calls)
        self.assertIn(["physical.updateNotePressure", 48, 106, 0], calls)
        self.assertIn(["physical.updateNotePressure", 48, 0, 0], calls)
        self.assertFalse(any(call[0] == "setExpression" for call in calls), calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI physical per-note pressure updated C3 pressure=106 channel=3", log)
        self.assertNotIn("SSLI physical expression native pressure", log)

    def test_regression_physical_concurrent_voices_use_shaped_velocity_not_max_velocity(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const instruments = [{ type: 'physical', settings: { volume: 100, physicalSettings: { model: 'bow' }, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            physical: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst]); activeOscs.set(midi, { physical: true }); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); activeOscs.delete(midi); },
              updateNotePressure(midi, pressure, inst) { window.__ssliCalls.push(['physical.updateNotePressure', midi, pressure, inst]); },
              allNotesOff(inst) { window.__ssliCalls.push(['physical.allNotesOff', inst]); activeOscs.clear(); }
            },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'physical'; },
              getInstruments() { return instruments; },
              getVoicePoolStats() { return { totalAllocated: 80, peakUsage: 1, steals: 0, currentlyActive: 0, available: 80 }; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); window.SynthLab.physical.noteOn(midi, velocity, 0); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); window.SynthLab.physical.noteOff(midi, 0); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        for raw, channel in [(48, 2), (52, 8), (55, 14)]:
            self.page.evaluate("(args) => window.__mockExquisInput.onmidimessage({ data: [0x90 | args.channel, args.raw, 54] })", {"raw": raw, "channel": channel})
        calls = self.page.evaluate("() => window.__ssliCalls")
        starts = [call for call in calls if call[0] == "startSustainedNote"]
        self.assertEqual(len(starts), 3, calls)
        self.assertTrue(all(call[2] < 100 for call in starts), calls)
        self.assertFalse(any(call[2] == 127 for call in starts), calls)
        self.assertEqual([call[2] for call in starts], [81, 81, 45], calls)
        self.assertLessEqual(len([call for call in calls if call[0] == "stopAllSustained"]), 1, calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI physical velocity shaped raw=54", log)
        self.assertIn("heldPhysical=2", log)

    def test_regression_two_simultaneous_physical_notes_keep_shared_attack_velocity(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const instruments = [{ type: 'physical', settings: { volume: 100, physicalSettings: { model: 'pluck' }, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            physical: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst]); activeOscs.set(midi, { physical: true }); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); activeOscs.delete(midi); },
              allNotesOff(inst) { window.__ssliCalls.push(['physical.allNotesOff', inst]); activeOscs.clear(); }
            },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'physical'; },
              getInstruments() { return instruments; },
              getVoicePoolStats() { return { totalAllocated: 80, peakUsage: 1, steals: 0, currentlyActive: 0, available: 80 }; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); window.SynthLab.physical.noteOn(midi, velocity, 0); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); window.SynthLab.physical.noteOff(midi, 0); },
              setExpression() {},
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x91, 53, 115] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x93, 50, 117] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        starts = [call for call in calls if call[0] == "startSustainedNote"]
        self.assertEqual([call[1:] for call in starts], [[53, 96], [50, 96]], calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("heldPhysical=1 effectiveHeld=0 model=pluck", log)

    def test_regression_adjacent_pluck_uses_general_voice_load_policy(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const instruments = [{ type: 'physical', settings: { volume: 100, physicalSettings: { model: 'pluck' }, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            physical: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst]); activeOscs.set(midi, { physical: true }); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); activeOscs.delete(midi); },
              allNotesOff(inst) { window.__ssliCalls.push(['physical.allNotesOff', inst]); activeOscs.clear(); }
            },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'physical'; },
              getInstruments() { return instruments; },
              getVoicePoolStats() { return { totalAllocated: 80, peakUsage: 1, steals: 0, currentlyActive: 0, available: 80 }; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); window.SynthLab.physical.noteOn(midi, velocity, 0); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); window.SynthLab.physical.noteOff(midi, 0); },
              setExpression() {},
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x99, 47, 60] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x94, 48, 86] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        starts = [call for call in calls if call[0] == "startSustainedNote"]
        self.assertEqual([call[1:] for call in starts], [[47, 90], [48, 96]], calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("heldPhysical=1 effectiveHeld=0 model=pluck", log)
        self.assertNotIn("semitoneJamGuard", log)

    def test_regression_four_note_physical_voices_track_pressure_independently_without_global_expression(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const instruments = [{ type: 'physical', settings: { volume: 100, physicalSettings: { model: 'bow' }, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            physical: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst]); activeOscs.set(midi, { physical: true }); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); activeOscs.delete(midi); },
              updateNotePressure(midi, pressure, inst) { window.__ssliCalls.push(['physical.updateNotePressure', midi, pressure, inst]); },
              allNotesOff(inst) { window.__ssliCalls.push(['physical.allNotesOff', inst]); activeOscs.clear(); }
            },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'physical'; },
              getInstruments() { return instruments; },
              getVoicePoolStats() { return { totalAllocated: 80, peakUsage: 1, steals: 0, currentlyActive: 0, available: 80 }; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); window.SynthLab.physical.noteOn(midi, velocity, 0); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); window.SynthLab.physical.noteOff(midi, 0); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        for raw, channel in [(47, 13), (50, 5), (53, 11), (57, 6)]:
            self.page.evaluate("(args) => window.__mockExquisInput.onmidimessage({ data: [0x90 | args.channel, args.raw, 110] })", {"raw": raw, "channel": channel})
            self.page.evaluate("(args) => window.__mockExquisInput.onmidimessage({ data: [0xD0 | args.channel, 127] })", {"channel": channel})
        calls = self.page.evaluate("() => window.__ssliCalls")
        starts = [call for call in calls if call[0] == "startSustainedNote"]
        self.assertEqual([call[2] for call in starts], [96, 96, 54, 42], calls)
        pressure_updates = [call for call in calls if call[0] == "physical.updateNotePressure"]
        self.assertEqual(
            pressure_updates,
            [
                ["physical.updateNotePressure", 47, 127, 0],
                ["physical.updateNotePressure", 50, 127, 0],
                ["physical.updateNotePressure", 53, 127, 0],
                ["physical.updateNotePressure", 57, 127, 0],
            ],
            calls,
        )
        self.assertFalse(any(call[0] == "setExpression" for call in calls), calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI physical per-note pressure updated B2 pressure=127 channel=14", log)
        self.assertIn("SSLI physical per-note pressure updated D3 pressure=127 channel=6", log)
        self.assertIn("SSLI physical per-note pressure updated F3 pressure=127 channel=12", log)
        self.assertIn("SSLI physical per-note pressure updated A3 pressure=127 channel=7", log)
        self.assertNotIn("per-note pressure unavailable", log)
        self.assertNotIn("SSLI physical expression native pressure", log)

    def test_regression_six_note_physical_voices_keep_independent_pressure_updates(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const instruments = [{ type: 'physical', settings: { volume: 100, physicalSettings: { model: 'bow' }, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            physical: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst]); activeOscs.set(midi, { physical: true }); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); activeOscs.delete(midi); },
              updateNotePressure(midi, pressure, inst) { window.__ssliCalls.push(['physical.updateNotePressure', midi, pressure, inst]); },
              allNotesOff(inst) { window.__ssliCalls.push(['physical.allNotesOff', inst]); activeOscs.clear(); }
            },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'physical'; },
              getInstruments() { return instruments; },
              getVoicePoolStats() { return { totalAllocated: 80, peakUsage: 1, steals: 0, currentlyActive: 0, available: 80 }; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); window.SynthLab.physical.noteOn(midi, velocity, 0); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); window.SynthLab.physical.noteOff(midi, 0); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        six_notes = [(48, 14), (50, 4), (52, 6), (53, 15), (55, 11), (57, 7)]
        for raw, channel in six_notes:
            self.page.evaluate("(args) => window.__mockExquisInput.onmidimessage({ data: [0x90 | args.channel, args.raw, 108] })", {"raw": raw, "channel": channel})
            self.page.evaluate("(args) => window.__mockExquisInput.onmidimessage({ data: [0xD0 | args.channel, 120] })", {"channel": channel})
        calls = self.page.evaluate("() => window.__ssliCalls")
        starts = [call for call in calls if call[0] == "startSustainedNote"]
        self.assertEqual([call[2] for call in starts], [96, 96, 54, 42, 42, 36], calls)
        pressure_updates = [call for call in calls if call[0] == "physical.updateNotePressure"]
        self.assertEqual(
            pressure_updates,
            [
                ["physical.updateNotePressure", 48, 120, 0],
                ["physical.updateNotePressure", 50, 120, 0],
                ["physical.updateNotePressure", 52, 120, 0],
                ["physical.updateNotePressure", 53, 120, 0],
                ["physical.updateNotePressure", 55, 120, 0],
                ["physical.updateNotePressure", 57, 120, 0],
            ],
            calls,
        )
        self.assertFalse(any(call[0] == "setExpression" for call in calls), calls)
        self.assertFalse(any(call[0] == "stopAllSustained" and call[1] > 0 for call in calls), calls)

    def test_regression_physical_pressure_stream_is_rate_limited_per_note_but_release_passes(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const instruments = [{ type: 'physical', settings: { volume: 100, physicalSettings: { model: 'bow' }, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            physical: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst]); activeOscs.set(midi, { physical: true }); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); activeOscs.delete(midi); },
              updateNotePressure(midi, pressure, inst) { window.__ssliCalls.push(['physical.updateNotePressure', midi, pressure, inst]); },
              allNotesOff(inst) { window.__ssliCalls.push(['physical.allNotesOff', inst]); activeOscs.clear(); }
            },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'physical'; },
              getInstruments() { return instruments; },
              getVoicePoolStats() { return { totalAllocated: 80, peakUsage: 1, steals: 0, currentlyActive: 0, available: 80 }; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); window.SynthLab.physical.noteOn(midi, velocity, 0); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); window.SynthLab.physical.noteOff(midi, 0); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => { window.__fixedNow = 100000; Date.now = () => window.__fixedNow; }")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x97, 48, 96] })")
        for pressure in [101, 104, 107, 109, 111, 113, 0]:
            self.page.evaluate("(pressure) => window.__mockExquisInput.onmidimessage({ data: [0xD7, pressure] })", pressure)
        calls = self.page.evaluate("() => window.__ssliCalls")
        pressure_updates = [call for call in calls if call[0] == "physical.updateNotePressure"]
        self.assertEqual(
            pressure_updates,
            [
                ["physical.updateNotePressure", 48, 101, 0],
                ["physical.updateNotePressure", 48, 0, 0],
            ],
            calls,
        )
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI physical per-note pressure skipped C3", log)

    def test_regression_plucked_physical_pressure_is_forwarded_per_note_to_audio_engine(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const instruments = [{ type: 'physical', settings: { volume: 100, physicalSettings: { model: 'pluck' }, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            physical: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst]); activeOscs.set(midi, { physical: true }); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst]); activeOscs.delete(midi); },
              updateNotePressure(midi, pressure, inst) { window.__ssliCalls.push(['physical.updateNotePressure', midi, pressure, inst]); },
              allNotesOff(inst) { window.__ssliCalls.push(['physical.allNotesOff', inst]); activeOscs.clear(); }
            },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'physical'; },
              getInstruments() { return instruments; },
              getVoicePoolStats() { return { totalAllocated: 80, peakUsage: 1, steals: 0, currentlyActive: 0, available: 80 }; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              setInstrumentVolume() {},
              getFinalDestination() { return { name: 'destination' }; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); window.SynthLab.physical.noteOn(midi, velocity, 0); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); window.SynthLab.physical.noteOff(midi, 0); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x97, 48, 96] })")
        for pressure in [101, 104, 120, 0]:
            self.page.evaluate("(pressure) => window.__mockExquisInput.onmidimessage({ data: [0xD7, pressure] })", pressure)
        calls = self.page.evaluate("() => window.__ssliCalls")
        pressure_updates = [call for call in calls if call[0] == "physical.updateNotePressure"]
        self.assertEqual(
            pressure_updates,
            [
                ["physical.updateNotePressure", 48, 101, 0],
                ["physical.updateNotePressure", 48, 120, 0],
                ["physical.updateNotePressure", 48, 0, 0],
            ],
            calls,
        )
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI physical per-note pressure updated C3", log)
        self.assertNotIn("SSLI physical pluck pressure bypassed", log)

    def test_regression_six_note_physical_pressure_flow_has_stable_final_audio_output(self):
        from tools.preset_signature_check import start_server

        server, url = start_server()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.page.goto(url)
        self.page.wait_for_selector('[data-testid="sound-engine-select"]')
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__sixNoteMidiInput = { id: 'six-note-exquis', name: 'Six Note Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__sixNoteMidiInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__sixNoteMidiInput && window.__sixNoteMidiInput.onmidimessage")
        self.page.wait_for_function("""() => [...document.querySelectorAll('[data-testid="sound-engine-select"] option')]
          .some(option => option.value === 'physical' || option.value === 'Physical' || option.textContent.trim() === 'Physical')""")
        self.page.select_option('[data-testid="sound-engine-select"]', label="Physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Bowed")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Violin")
        metrics = self.page.evaluate("""
        async () => {
          const input = window.__sixNoteMidiInput;
          input.onmidimessage({ data: [0x97, 48, 107] });
          await new Promise(resolve => setTimeout(resolve, 30));
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow;
          const SL = host && host.SynthLab;
          const ctx = SL && SL.audio && SL.audio.getCtx ? SL.audio.getCtx() : null;
          const masterOutput = SL && SL.audio && SL.audio.getInstruments && SL.audio.getInstruments()[0] && SL.audio.getInstruments()[0].masterOutput;
          if (!ctx || !masterOutput) return { available: false, error: 'missing SSLI master output path' };
          const analyser = ctx.createAnalyser();
          analyser.fftSize = 2048;
          masterOutput.connect(analyser);
          const wave = new Uint8Array(analyser.fftSize);
          const spectrum = new Uint8Array(analyser.frequencyBinCount);
          const events = [
            [0, [0x9C, 52, 109]], [6, [0x91, 53, 119]], [12, [0x9F, 55, 93]], [18, [0x92, 57, 126]], [24, [0x9A, 50, 126]],
            [35, [0xD7, 107]], [38, [0xDC, 109]], [41, [0xD1, 119]], [44, [0xDF, 93]], [47, [0xD2, 126]], [50, [0xDA, 126]],
            [60, [0xD7, 101]], [63, [0xDC, 106]], [66, [0xD1, 118]], [69, [0xDF, 85]], [72, [0xD2, 122]], [75, [0xDA, 119]],
            [85, [0xD7, 93]], [88, [0xDC, 103]], [91, [0xD1, 115]], [94, [0xDF, 68]], [97, [0xD2, 113]], [100, [0xDA, 95]],
            [115, [0xDF, 0]], [125, [0x8F, 55, 0]], [135, [0xD7, 0]], [145, [0x87, 48, 0]], [155, [0xDC, 0]], [165, [0x8C, 52, 0]],
            [175, [0xD2, 0]], [185, [0x82, 57, 0]], [195, [0xD1, 0]], [205, [0x81, 53, 0]], [215, [0xDA, 0]], [225, [0x8A, 50, 0]]
          ];
          events.forEach(([delay, data]) => setTimeout(() => input.onmidimessage({ data }), delay));
          let peak = 0;
          let rmsSum = 0;
          let count = 0;
          let clipped = 0;
          let spectrumPeak = 0;
          let spectrumSum = 0;
          let spectrumCount = 0;
          const framePeaks = [];
          const start = Date.now();
          while (Date.now() - start < 900) {
            analyser.getByteTimeDomainData(wave);
            analyser.getByteFrequencyData(spectrum);
            let framePeak = 0;
            for (let i = 0; i < wave.length; i += 1) {
              const n = (wave[i] - 128) / 128;
              const abs = Math.abs(n);
              peak = Math.max(peak, abs);
              framePeak = Math.max(framePeak, abs);
              rmsSum += n * n;
              count += 1;
              if (wave[i] <= 2 || wave[i] >= 253) clipped += 1;
            }
            framePeaks.push(framePeak);
            for (let j = 0; j < spectrum.length; j += 1) {
              const s = spectrum[j] / 255;
              spectrumPeak = Math.max(spectrumPeak, s);
              spectrumSum += s * s;
              spectrumCount += 1;
            }
            await new Promise(resolve => setTimeout(resolve, 16));
          }
          try { masterOutput.disconnect(analyser); } catch (err) {}
          framePeaks.sort((a, b) => a - b);
          return {
            available: true,
            peak: Number(peak.toFixed(5)),
            rms: Number(Math.sqrt(rmsSum / Math.max(1, count)).toFixed(5)),
            clipRatio: Number((clipped / Math.max(1, count)).toFixed(6)),
            p95Peak: Number(framePeaks[Math.floor(framePeaks.length * 0.95)].toFixed(5)),
            spectrumPeak: Number(spectrumPeak.toFixed(5)),
            spectrumRms: Number(Math.sqrt(spectrumSum / Math.max(1, spectrumCount)).toFixed(5)),
            finalOutputGain: Number(masterOutput.gain && typeof masterOutput.gain.value === 'number' ? masterOutput.gain.value.toFixed(2) : 1),
            diagnosticLog: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
        }
        """)
        self.assertTrue(metrics.get("available"), metrics)
        self.assertIn("SSLI physical per-note pressure updated", metrics["diagnosticLog"])
        self.assertNotIn("SSLI physical pluck pressure bypassed", metrics["diagnosticLog"])
        self.assertLessEqual(metrics["finalOutputGain"], 1.8, metrics)
        self.assertLessEqual(metrics["peak"], 0.55, metrics)
        self.assertLessEqual(metrics["p95Peak"], 0.38, metrics)
        self.assertLessEqual(metrics["clipRatio"], 0.0005, metrics)
        self.assertLessEqual(metrics["spectrumPeak"], 0.98, metrics)
        self.assertGreater(metrics["rms"], 0.015, metrics)

    def test_regression_adjacent_pluck_has_stable_audio_output(self):
        from tools.preset_signature_check import start_server

        server, url = start_server()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.page.goto(url)
        self.page.wait_for_selector('[data-testid="sound-engine-select"]')
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__twoNoteMidiInput = { id: 'two-note-exquis', name: 'Two Note Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__twoNoteMidiInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__twoNoteMidiInput && window.__twoNoteMidiInput.onmidimessage")
        self.page.select_option('[data-testid="sound-engine-select"]', label="Physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        metrics = self.page.evaluate("""
        async () => {
          const input = window.__twoNoteMidiInput;
          const events = [
            [0, [0x99, 47, 60]], [2, [0x94, 48, 86]],
            [18, [0xD9, 99]], [20, [0xD4, 62]],
            [60, [0xD9, 104]], [62, [0xD4, 104]],
            [130, [0xD9, 81]], [132, [0xD4, 101]],
            [210, [0xD9, 32]], [212, [0xD4, 68]],
            [280, [0xD9, 0]], [282, [0xD4, 0]],
            [290, [0x89, 47, 0]], [292, [0x84, 48, 0]]
          ];
          events.forEach(([delay, data]) => setTimeout(() => input.onmidimessage({ data }), delay));
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow;
          const SL = host && host.SynthLab;
          const waitStart = Date.now();
          while (Date.now() - waitStart < 500 && !(SL && SL.audio && SL.audio.getInstruments && SL.audio.getInstruments()[0] && SL.audio.getInstruments()[0].masterOutput)) {
            await new Promise(resolve => setTimeout(resolve, 10));
          }
          const ctx = SL && SL.audio && SL.audio.getCtx ? SL.audio.getCtx() : null;
          const masterOutput = SL && SL.audio && SL.audio.getInstruments && SL.audio.getInstruments()[0] && SL.audio.getInstruments()[0].masterOutput;
          if (!ctx || !masterOutput) return { available: false, error: 'missing SSLI master output path' };
          const analyser = ctx.createAnalyser();
          analyser.fftSize = 2048;
          masterOutput.connect(analyser);
          const wave = new Uint8Array(analyser.fftSize);
          const spectrum = new Uint8Array(analyser.frequencyBinCount);
          let peak = 0;
          let rmsSum = 0;
          let count = 0;
          let clipped = 0;
          let spectrumPeak = 0;
          let spectrumSum = 0;
          let spectrumCount = 0;
          const framePeaks = [];
          const start = Date.now();
          while (Date.now() - start < 520) {
            analyser.getByteTimeDomainData(wave);
            analyser.getByteFrequencyData(spectrum);
            let framePeak = 0;
            for (let i = 0; i < wave.length; i += 1) {
              const n = (wave[i] - 128) / 128;
              const abs = Math.abs(n);
              peak = Math.max(peak, abs);
              framePeak = Math.max(framePeak, abs);
              rmsSum += n * n;
              count += 1;
              if (wave[i] <= 2 || wave[i] >= 253) clipped += 1;
            }
            framePeaks.push(framePeak);
            for (let j = 0; j < spectrum.length; j += 1) {
              const s = spectrum[j] / 255;
              spectrumPeak = Math.max(spectrumPeak, s);
              spectrumSum += s * s;
              spectrumCount += 1;
            }
            await new Promise(resolve => setTimeout(resolve, 16));
          }
          try { masterOutput.disconnect(analyser); } catch (err) {}
          framePeaks.sort((a, b) => a - b);
          return {
            available: true,
            peak: Number(peak.toFixed(5)),
            rms: Number(Math.sqrt(rmsSum / Math.max(1, count)).toFixed(5)),
            clipRatio: Number((clipped / Math.max(1, count)).toFixed(6)),
            p95Peak: Number(framePeaks[Math.floor(framePeaks.length * 0.95)].toFixed(5)),
            spectrumPeak: Number(spectrumPeak.toFixed(5)),
            spectrumRms: Number(Math.sqrt(spectrumSum / Math.max(1, spectrumCount)).toFixed(5)),
            finalOutputGain: Number(masterOutput.gain && typeof masterOutput.gain.value === 'number' ? masterOutput.gain.value.toFixed(2) : 1),
            diagnosticLog: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
        }
        """)
        self.assertTrue(metrics.get("available"), metrics)
        self.assertIn("articulation queued B2 mode=strum", metrics["diagnosticLog"])
        self.assertIn("articulation queued C3 mode=strum", metrics["diagnosticLog"])
        self.assertIn("articulation flush mode=strum", metrics["diagnosticLog"])
        self.assertNotIn("semitoneJamGuard", metrics["diagnosticLog"])
        self.assertIn("SSLI plucked one-shot B2 velocity=50", metrics["diagnosticLog"])
        self.assertIn("SSLI plucked one-shot C3 velocity=54", metrics["diagnosticLog"])
        self.assertIn("SSLI plucked pressure ignored after onset", metrics["diagnosticLog"])
        self.assertLessEqual(metrics["peak"], 0.55, metrics)
        self.assertLessEqual(metrics["p95Peak"], 0.5, metrics)
        self.assertLessEqual(metrics["clipRatio"], 0.0005, metrics)
        self.assertLessEqual(metrics["spectrumPeak"], 0.92, metrics)
        self.assertGreater(metrics["rms"], 0.01, metrics)

    def test_regression_three_note_plucked_strum_has_stable_audio_output(self):
        from tools.preset_signature_check import start_server

        server, url = start_server()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.page.goto(url)
        self.page.wait_for_selector('[data-testid="sound-engine-select"]')
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__threeNoteMidiInput = { id: 'three-note-exquis', name: 'Three Note Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__threeNoteMidiInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__threeNoteMidiInput && window.__threeNoteMidiInput.onmidimessage")
        self.page.select_option('[data-testid="sound-engine-select"]', label="Physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        metrics = self.page.evaluate("""
        async () => {
          const input = window.__threeNoteMidiInput;
          const events = [
            [0, [0x96, 48, 72]], [2, [0xD6, 99]],
            [4, [0x9D, 52, 74]], [6, [0xDD, 104]],
            [8, [0x9F, 55, 69]], [10, [0xDF, 94]],
            [42, [0xD6, 101]], [44, [0xDD, 107]], [46, [0xDF, 91]],
            [82, [0xD6, 89]], [84, [0xDD, 82]], [86, [0xDF, 80]],
            [118, [0xD6, 0]], [120, [0x86, 48, 0]],
            [138, [0xDD, 0]], [140, [0x8D, 52, 0]],
            [158, [0xDF, 0]], [160, [0x8F, 55, 0]]
          ];
          events.forEach(([delay, data]) => setTimeout(() => input.onmidimessage({ data }), delay));
          await new Promise(resolve => setTimeout(resolve, 95));
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow;
          const SL = host && host.SynthLab;
          const ctx = SL && SL.audio && SL.audio.getCtx ? SL.audio.getCtx() : null;
          const masterOutput = SL && SL.audio && SL.audio.getInstruments && SL.audio.getInstruments()[0] && SL.audio.getInstruments()[0].masterOutput;
          if (!ctx || !masterOutput) return { available: false, error: 'missing SSLI master output path' };
          const analyser = ctx.createAnalyser();
          analyser.fftSize = 2048;
          masterOutput.connect(analyser);
          const wave = new Uint8Array(analyser.fftSize);
          const spectrum = new Uint8Array(analyser.frequencyBinCount);
          let peak = 0;
          let rmsSum = 0;
          let count = 0;
          let clipped = 0;
          let spectrumPeak = 0;
          const start = Date.now();
          while (Date.now() - start < 430) {
            analyser.getByteTimeDomainData(wave);
            analyser.getByteFrequencyData(spectrum);
            for (let i = 0; i < wave.length; i += 1) {
              const n = (wave[i] - 128) / 128;
              const abs = Math.abs(n);
              peak = Math.max(peak, abs);
              rmsSum += n * n;
              count += 1;
              if (wave[i] <= 2 || wave[i] >= 253) clipped += 1;
            }
            for (let j = 0; j < spectrum.length; j += 1) spectrumPeak = Math.max(spectrumPeak, spectrum[j] / 255);
            await new Promise(resolve => setTimeout(resolve, 16));
          }
          try { masterOutput.disconnect(analyser); } catch (err) {}
          return {
            available: true,
            peak: Number(peak.toFixed(5)),
            rms: Number(Math.sqrt(rmsSum / Math.max(1, count)).toFixed(5)),
            clipRatio: Number((clipped / Math.max(1, count)).toFixed(6)),
            spectrumPeak: Number(spectrumPeak.toFixed(5)),
            finalOutputGain: Number(masterOutput.gain && typeof masterOutput.gain.value === 'number' ? masterOutput.gain.value.toFixed(2) : 1),
            diagnosticLog: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
        }
        """)
        self.assertTrue(metrics.get("available"), metrics)
        self.assertIn("articulation flush mode=strum", metrics["diagnosticLog"])
        self.assertIn("SSLI plucked one-shot", metrics["diagnosticLog"])
        self.assertIn("SSLI plucked pressure ignored after onset", metrics["diagnosticLog"])
        self.assertNotIn("SSLI output boost", metrics["diagnosticLog"])
        self.assertLessEqual(metrics["peak"], 0.55, metrics)
        self.assertLessEqual(metrics["clipRatio"], 0.0005, metrics)
        self.assertLessEqual(metrics["spectrumPeak"], 0.95, metrics)
        self.assertGreater(metrics["rms"], 0.006, metrics)

    def test_regression_real_plucked_strum_plays_note_released_after_flush_before_slot(self):
        from tools.preset_signature_check import start_server

        server, url = start_server()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.page.goto(url)
        self.page.wait_for_selector('[data-testid="sound-engine-select"]')
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__quickReleaseMidiInput = { id: 'quick-release-exquis', name: 'Quick Release Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__quickReleaseMidiInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__quickReleaseMidiInput && window.__quickReleaseMidiInput.onmidimessage")
        self.page.select_option('[data-testid="sound-engine-select"]', label="Physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.page.evaluate("""
        async () => {
          const input = window.__quickReleaseMidiInput;
          const events = [
            [0, [0x98, 59, 57]], [1, [0xD8, 84]],
            [3, [0x92, 55, 37]], [4, [0xD2, 26]],
            [6, [0x9E, 52, 68]], [7, [0xDE, 88]],
            [34, [0xDE, 0]], [35, [0x8E, 52, 0]],
            [52, [0xD2, 0]], [53, [0x82, 55, 0]],
            [55, [0xD8, 0]], [56, [0x88, 59, 0]]
          ];
          events.forEach(([delay, data]) => setTimeout(() => input.onmidimessage({ data }), delay));
          await new Promise(resolve => setTimeout(resolve, 120));
        }
        """)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("articulation flush mode=strum family=plucked notes=B3,G3,E3", log)
        self.assertIn("SSLI plucked one-shot B3", log)
        self.assertIn("SSLI plucked one-shot G3", log)
        self.assertIn("SSLI plucked one-shot E3", log)
        self.assertNotIn("articulation skipped released E3", log)

    def install_articulation_mock(self, instrument_type="physical", physical_model="pluck"):
        self.page.evaluate("""
        ([instrumentType, physicalModel]) => {
          window.__ssliCalls = [];
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          const originalDestination = { name: 'originalDestination' };
          const mockGainNode = {
            name: 'mockGain',
            gain: { value: 1 },
            connect(target) { window.__ssliCalls.push(['mockGainConnect', target.name || 'target', performance.now()]); }
          };
          const instrument = {
            type: instrumentType,
            settings: {
              volume: 100,
              physicalSettings: { model: physicalModel, excitation: 'pick' },
              filter: {},
              effects: {}
            }
          };
          const runtimePreset = {
            name: instrumentType === 'physical' ? 'Nylon Guitar' : 'Soft EP',
            category: instrumentType === 'physical' ? 'Plucked' : 'Keys',
            engine: instrumentType,
            settings: instrument.settings
          };
          window.SynthLab = {
            presets: {
              getEngines() { return [instrumentType]; },
              getCategoriesForEngine() { return [runtimePreset.category]; },
              getPresetsForEngineCategory() { return [runtimePreset]; },
              apply() { window.__ssliCalls.push(['apply', performance.now()]); }
            },
            audio: {
              getCtx() { return { state: 'running', currentTime: performance.now() / 1000, createGain() { return mockGainNode; } }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return instrument.type; },
              getInstruments() { return [instrument]; },
              setInstrumentVolume(inst, volume) { instrument.settings.volume = volume; window.__ssliCalls.push(['setInstrumentVolume', volume, performance.now()]); },
              getFinalDestination() { return originalDestination; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', performance.now()]); },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              playNoteOnInstrument(midi, dur, inst, vel) { window.__ssliCalls.push(['playNoteOnInstrument', midi, dur, inst, vel, performance.now()]); },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity, performance.now()]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi, performance.now()]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3)), performance.now()]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression', performance.now()]); }
            },
            physical: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst, performance.now()]); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst, performance.now()]); },
              updateNotePressure(midi, pressure, inst) { window.__ssliCalls.push(['physical.updateNotePressure', midi, pressure, inst, performance.now()]); },
              allNotesOff() {}
            }
          };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """, [instrument_type, physical_model])

    def test_regression_plucked_presets_buffer_simultaneous_note_ons_into_strum(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__strumStart = performance.now();
          window.__mockExquisInput.onmidimessage({ data: [0x91, 47, 90] });
          window.__mockExquisInput.onmidimessage({ data: [0x92, 48, 90] });
          window.__mockExquisInput.onmidimessage({ data: [0xD1, 111] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 2")
        metrics = self.page.evaluate("""
        () => {
          const starts = window.__ssliCalls.filter(call => call[0] === 'physical.noteOn');
          const sustained = window.__ssliCalls.filter(call => call[0] === 'startSustainedNote');
          const physicalOff = window.__ssliCalls.filter(call => call[0] === 'physical.noteOff');
          const pressure = window.__ssliCalls.filter(call => call[0] === 'physical.updateNotePressure');
          return {
            starts,
            sustained,
            physicalOff,
            firstDelay: starts[0][4] - window.__strumStart,
            spacing: starts[1][4] - starts[0][4],
            log: document.querySelector('[data-testid="diagnostic-log"]').textContent,
            pressure
          };
        }
        """)
        self.assertEqual([call[1] for call in metrics["starts"]], [47, 48], metrics)
        self.assertEqual(metrics["sustained"], [], metrics)
        self.assertEqual(metrics["physicalOff"], [], metrics)
        self.assertGreaterEqual(metrics["firstDelay"], 12, metrics)
        self.assertGreaterEqual(metrics["spacing"], 8, metrics)
        self.assertLessEqual(metrics["spacing"], 46, metrics)
        self.assertIn("articulation queued B2 mode=strum", metrics["log"])
        self.assertIn("articulation flush mode=strum", metrics["log"])
        self.assertEqual(metrics["pressure"], [], metrics)
        self.assertIn("SSLI plucked pressure ignored after onset B2", metrics["log"])

    def test_regression_plucked_strum_uses_group_headroom_from_first_note(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x9A, 53, 43] });
          window.__mockExquisInput.onmidimessage({ data: [0x9D, 47, 71] });
          window.__mockExquisInput.onmidimessage({ data: [0x96, 50, 67] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 3")
        calls = self.page.evaluate("() => window.__ssliCalls")
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("articulation flush mode=strum", log)
        self.assertEqual([call[0] for call in calls if call[0] == "startSustainedNote"], [], calls)
        self.assertEqual([call[0] for call in calls if call[0] == "physical.noteOff"], [], calls)
        self.assertIn("SSLI plucked one-shot", log)
        self.assertNotIn("SSLI output boost", log)

    def test_regression_plucked_strum_ignores_held_pressure_and_auto_damps(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x92, 48, 81] });
          window.__mockExquisInput.onmidimessage({ data: [0x9E, 52, 83] });
          window.__mockExquisInput.onmidimessage({ data: [0x9C, 55, 53] });
          window.__mockExquisInput.onmidimessage({ data: [0xD2, 127] });
          window.__mockExquisInput.onmidimessage({ data: [0xDE, 112] });
          window.__mockExquisInput.onmidimessage({ data: [0xDC, 100] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 3")
        self.page.wait_for_timeout(430)
        metrics = self.page.evaluate("""
        () => ({
          pressure: window.__ssliCalls.filter(call => call[0] === 'physical.updateNotePressure'),
          stops: window.__ssliCalls.filter(call => call[0] === 'stopSustainedNote'),
          physicalOff: window.__ssliCalls.filter(call => call[0] === 'physical.noteOff'),
          sustained: window.__ssliCalls.filter(call => call[0] === 'startSustainedNote'),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual(metrics["pressure"], [], metrics)
        self.assertEqual(metrics["stops"], [], metrics)
        self.assertEqual(metrics["physicalOff"], [], metrics)
        self.assertEqual(metrics["sustained"], [], metrics)
        self.assertIn("SSLI plucked pressure ignored after onset", metrics["log"])
        self.assertIn("SSLI plucked one-shot natural decay", metrics["log"])
        self.assertIn("SSLI plucked one-shot", metrics["log"])

    def test_regression_plucked_held_one_shot_keeps_voice_ownership_until_note_off(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          const input = window.__mockExquisInput;
          input.onmidimessage({ data: [0x92, 47, 101] });
          input.onmidimessage({ data: [0xD2, 127] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 1")
        self.page.wait_for_timeout(480)
        mid_hold = self.page.evaluate("""
        () => ({
          debug: window.__exquisDebugSnapshot(),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent,
          physicalOff: window.__ssliCalls.filter(call => call[0] === 'physical.noteOff')
        })
        """)
        self.assertEqual(mid_hold["debug"]["heldNotes"], 1, mid_hold)
        self.assertEqual(mid_hold["debug"]["midiVoices"], 1, mid_hold)
        self.assertNotIn("after-one-shot-expire B2 held=1 local=0", mid_hold["log"])
        self.assertEqual([call[1] for call in mid_hold["physicalOff"]], [47], mid_hold)
        self.page.evaluate("""
        () => {
          const input = window.__mockExquisInput;
          input.onmidimessage({ data: [0xD2, 0] });
          input.onmidimessage({ data: [0x82, 47, 0] });
        }
        """)
        self.page.wait_for_timeout(40)
        after_release = self.page.evaluate("() => window.__exquisDebugSnapshot()")
        self.assertEqual(after_release["heldNotes"], 0, after_release)
        self.assertEqual(after_release["midiVoices"], 0, after_release)

    def test_regression_non_plucked_presets_keep_immediate_note_ons(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "subtractive")
        self.page.select_option('[data-testid="sound-category-select"]', "Keys")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Soft EP")
        self.install_articulation_mock("subtractive", "")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__immediateStart = performance.now();
          window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 90] });
          window.__afterFirstImmediateStarts = window.__ssliCalls.filter(call => call[0] === 'startSustainedNote').length;
          window.__mockExquisInput.onmidimessage({ data: [0x92, 52, 90] });
          window.__afterSecondImmediateStarts = window.__ssliCalls.filter(call => call[0] === 'startSustainedNote').length;
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'startSustainedNote').length >= 2")
        metrics = self.page.evaluate("""
        () => {
          const starts = window.__ssliCalls.filter(call => call[0] === 'startSustainedNote');
            return {
              starts,
              firstDelay: starts[0][3] - window.__immediateStart,
              spacing: starts[1][3] - starts[0][3],
              afterFirst: window.__afterFirstImmediateStarts,
              afterSecond: window.__afterSecondImmediateStarts,
              log: document.querySelector('[data-testid="diagnostic-log"]').textContent
            };
          }
        """)
        self.assertEqual([call[1] for call in metrics["starts"]], [48, 52], metrics)
        self.assertLess(metrics["firstDelay"], 12, metrics)
        self.assertEqual(metrics["afterFirst"], 1, metrics)
        self.assertEqual(metrics["afterSecond"], 2, metrics)
        self.assertNotIn("articulation queued", metrics["log"])

    def test_regression_released_buffered_strum_note_does_not_start_synth_voice(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 90] });
          window.__mockExquisInput.onmidimessage({ data: [0x81, 48, 0] });
        }
        """)
        self.page.wait_for_timeout(80)
        metrics = self.page.evaluate("""
        () => ({
          starts: window.__ssliCalls.filter(call => call[0] === 'physical.noteOn'),
          stops: window.__ssliCalls.filter(call => call[0] === 'stopSustainedNote'),
          physicalOff: window.__ssliCalls.filter(call => call[0] === 'physical.noteOff'),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual(metrics["starts"], [], metrics)
        self.assertEqual(metrics["stops"], [], metrics)
        self.assertEqual(metrics["physicalOff"], [], metrics)
        self.assertIn("articulation queued C3 mode=strum", metrics["log"])

    def test_regression_plucked_strum_plays_note_released_after_flush_before_slot(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          const input = window.__mockExquisInput;
          input.onmidimessage({ data: [0x98, 59, 57] });
          input.onmidimessage({ data: [0x92, 55, 37] });
          input.onmidimessage({ data: [0x9E, 52, 68] });
          setTimeout(() => input.onmidimessage({ data: [0x8E, 52, 0] }), 24);
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 3")
        metrics = self.page.evaluate("""
        () => ({
          starts: window.__ssliCalls.filter(call => call[0] === 'physical.noteOn'),
          sustained: window.__ssliCalls.filter(call => call[0] === 'startSustainedNote'),
          physicalOff: window.__ssliCalls.filter(call => call[0] === 'physical.noteOff'),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual([call[1] for call in metrics["starts"]], [59, 55, 52], metrics)
        self.assertEqual(metrics["sustained"], [], metrics)
        self.assertEqual(metrics["physicalOff"], [], metrics)
        self.assertIn("articulation flush mode=strum family=plucked notes=B3,G3,E3", metrics["log"])
        self.assertIn("SSLI plucked one-shot E3", metrics["log"])
        self.assertNotIn("articulation skipped released E3", metrics["log"])

    def test_regression_plucked_strum_plays_capture_matured_note_even_when_flush_timer_is_late(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.evaluate("""
        () => {
          const realSetTimeout = window.setTimeout.bind(window);
          window.__realSetTimeout = realSetTimeout;
          window.setTimeout = (fn, delay, ...args) => {
            const lateDelay = delay === 18 ? 58 : delay;
            return realSetTimeout(fn, lateDelay, ...args);
          };
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          const input = window.__mockExquisInput;
          input.onmidimessage({ data: [0x98, 59, 57] });
          input.onmidimessage({ data: [0x92, 55, 37] });
          input.onmidimessage({ data: [0x9E, 52, 68] });
          window.__realSetTimeout(() => input.onmidimessage({ data: [0x8E, 52, 0] }), 24);
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 3")
        metrics = self.page.evaluate("""
        () => ({
          starts: window.__ssliCalls.filter(call => call[0] === 'physical.noteOn'),
          sustained: window.__ssliCalls.filter(call => call[0] === 'startSustainedNote'),
          physicalOff: window.__ssliCalls.filter(call => call[0] === 'physical.noteOff'),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual([call[1] for call in metrics["starts"]], [59, 55, 52], metrics)
        self.assertEqual(metrics["sustained"], [], metrics)
        self.assertEqual(metrics["physicalOff"], [], metrics)
        self.assertIn("articulation flush mode=strum family=plucked notes=B3,G3,E3", metrics["log"])
        self.assertIn("SSLI plucked one-shot E3", metrics["log"])
        self.assertNotIn("articulation skipped released E3", metrics["log"])

    def test_regression_midi_reports_missing_ssli_runtime_api_before_local_fallback(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.SynthLab = {
            presets: {
              getEngines() { return ['Physical']; },
              getCategoriesForEngine() { return ['Plucked']; },
              getPresetsForEngineCategory() { return [{ name: 'Koto', category: 'Plucked', engine: 'physical', settings: { physicalSettings: { model: 'pluck' } } }]; },
              engineNameToType() { return 'physical'; }
            },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ type: 'subtractive', settings: {} }]; }
            }
          };
          document.getElementById('ssliEngineFrame').dispatchEvent(new Event('load'));
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.select_option('[data-testid="sound-engine-select"]', "Physical")
        self.page.select_option('[data-testid="sound-category-select"]', "Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Koto")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x92, 48, 64] })")
        self.page.wait_for_timeout(50)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI preset apply failed: missing SynthLab.presets.apply preset=Physical::Koto", log)
        self.assertIn("SSLI MIDI unavailable for C3: missing SynthLab.presets.apply", log)
        self.assertIn("MIDI voice start C3", log)

    def test_regression_preset_selection_retries_when_ssli_runtime_loads_late(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.__installLateSsli = () => {
            const instruments = [{ type: 'subtractive', settings: { filter: {}, effects: {}, physicalSettings: {} } }];
            window.SynthLab = {
              presets: {
                getEngines() { return ['Physical']; },
                getCategoriesForEngine() { return ['Plucked']; },
                getPresetsForEngineCategory() { return [{ name: 'Koto', category: 'Plucked', engine: 'physical', settings: { physicalSettings: { model: 'pluck' }, filter: {}, effects: {} } }]; },
                engineNameToType() { return 'physical'; },
                apply(preset, inst) {
                  instruments[inst || 0].type = preset.engine;
                  instruments[inst || 0].settings = JSON.parse(JSON.stringify(preset.settings));
                  window.__ssliCalls.push(['apply', preset.engine, preset.name]);
                }
              },
              state: { notify(kind) { window.__ssliCalls.push(['notify', kind]); } },
              audio: {
                getCtx() { return { state: 'running' }; },
                initEffectChain() {},
                getCurrentInstrument() { return 0; },
                getInstruments() { return instruments; },
                stopAllSustained() { window.__ssliCalls.push(['stopAllSustained']); }
              }
            };
          };
        }
        """)
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', "Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Koto")
        self.assertIn("SSLI preset apply failed: missing runtime host", self.page.locator('[data-testid="diagnostic-log"]').inner_text())
        self.page.evaluate("() => window.__installLateSsli()")
        self.page.wait_for_function("() => window.__ssliCalls && window.__ssliCalls.some(call => call[0] === 'apply' && call[1] === 'physical' && call[2] === 'Koto')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["apply", "physical", "Koto"], calls)
        self.assertIn("SSLI runtime became ready; retrying preset apply", self.page.locator('[data-testid="diagnostic-log"]').inner_text())

    def test_regression_filter_and_fx_controls_call_ssli_audio_api(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const effects = {};
          const chain = {
            getAvailableEffects() { return Object.keys(effects); },
            addToChain(name) {
              window.__ssliCalls.push(['addToChain', name]);
              effects[name] = effects[name] || {
                setEnabled(value) { window.__ssliCalls.push(['setEnabled', name, value]); },
                setParam(param, value) { window.__ssliCalls.push(['setParam', name, param, value]); }
              };
            },
            getEffect(name) {
              this.addToChain(name);
              return effects[name];
            },
            setOrder(order) { window.__ssliCalls.push(['setOrder', order.join(',')]); },
            setMasterMix(value) { window.__ssliCalls.push(['setMasterMix', value]); }
          };
          window.SynthLab = {
            presets: { apply(preset, inst) { window.__ssliCalls.push(['apply', preset.engine, preset.name, inst]); } },
            audio: {
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ settings: { filter: {}, effects: {} } }]; },
              getInstrumentChain() { return chain; },
              freqToSlider(value) { window.__ssliCalls.push(['freqToSlider', value]); return value / 100; },
              qToSlider(value) { window.__ssliCalls.push(['qToSlider', value]); return value * 10; },
              loadInstrumentSettings(inst) { window.__ssliCalls.push(['loadInstrumentSettings', inst]); },
              refreshFilter() { window.__ssliCalls.push(['refreshFilter']); },
              playNoteOnInstrument(midi, dur, inst, vel) { window.__ssliCalls.push(['play', midi, dur, inst, vel]); }
            }
          };
        }
        """)
        self.page.select_option('[data-testid="fx-category-select"]', "Performance / Live")
        self.page.select_option('[data-testid="fx-preset-select"]', "lead-solo")
        self.page.select_option('[data-testid="filter-type-select"]', "bandpass")
        self.page.locator('[data-testid="filter-cutoff"]').evaluate("(el) => { el.value = '6400'; el.dispatchEvent(new Event('input', { bubbles: true })); }")
        self.page.locator('[data-testid="filter-resonance"]').evaluate("(el) => { el.value = '9.5'; el.dispatchEvent(new Event('input', { bubbles: true })); }")
        self.page.locator('[data-testid="play-step"]').click()
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["freqToSlider", 6400], calls)
        self.assertIn(["qToSlider", 9.5], calls)
        self.assertIn(["loadInstrumentSettings", 0], calls)
        self.assertIn(["refreshFilter"], calls)
        self.assertIn(["setOrder", "distortion,delay,reverb"], calls)
        self.assertIn(["setEnabled", "distortion", True], calls)
        self.assertIn(["setParam", "delay", "time", 375], calls)
        self.assertIn(["setParam", "reverb", "mix", 15], calls)
        self.assertTrue(any(call[0] == "play" for call in calls))

    def test_regression_ssli_engine_initializes_before_selected_preset_playback(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            __wavetableReady: false,
            wavetableSynth: {
              init() { window.__ssliCalls.push(['wavetableInit']); window.SynthLab.__wavetableReady = true; }
            },
            presets: { apply(preset, inst) { window.__ssliCalls.push(['apply', preset.engine, preset.name, inst]); } },
            audio: {
              getCtx() { window.__ssliCalls.push(['getCtx']); return { state: 'running' }; },
              initEffectChain() { window.__ssliCalls.push(['initEffectChain']); },
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ settings: { filter: {}, effects: {} } }]; },
              getInstrumentChain() {
                return {
                  getAvailableEffects() { return []; },
                  addToChain() {},
                  getEffect() { return { setEnabled() {}, setParam() {} }; },
                  setOrder() {},
                  setMasterMix() {}
                };
              },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              playNoteOnInstrument(midi) {
                window.__ssliCalls.push(['play', midi, window.SynthLab.__wavetableReady]);
                if (!window.SynthLab.__wavetableReady) throw new Error('wavetable not initialized');
              }
            }
          };
        }
        """)
        self.page.locator('[data-testid="show-all-engines"]').check()
        self.page.select_option('[data-testid="sound-engine-select"]', "wavetable-synth")
        self.page.locator('[data-testid="play-step"]').click()
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["wavetableInit"], calls)
        self.assertTrue(any(call[0] == "play" and call[2] is True for call in calls), calls)

    def test_regression_exquis_midi_uses_ssli_sustained_note_and_expression_api(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: {
              apply(preset, inst) { window.__ssliCalls.push(['apply', preset.engine, preset.name, inst]); }
            },
            audio: {
              getCtx() { window.__ssliCalls.push(['getCtx']); return { state: 'running' }; },
              initEffectChain() { window.__ssliCalls.push(['initEffectChain']); },
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ settings: { filter: {}, effects: {} } }]; },
              loadInstrumentSettings(inst) { window.__ssliCalls.push(['loadInstrumentSettings', inst]); },
              refreshFilter() { window.__ssliCalls.push(['refreshFilter']); },
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() {
                return {
                  getAvailableEffects() { return []; },
                  addToChain(name) { window.__ssliCalls.push(['addToChain', name]); },
                  getEffect(name) {
                    return {
                      setEnabled(v) { window.__ssliCalls.push(['setEnabled', name, v]); },
                      setParam(k, v) { window.__ssliCalls.push(['setParam', name, k, v]); }
                    };
                  },
                  setOrder(order) { window.__ssliCalls.push(['setOrder', order.join(',')]); },
                  setMasterMix(v) { window.__ssliCalls.push(['setMasterMix', v]); }
                };
              },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); },
              playNoteOnInstrument(midi, dur, inst, vel) { window.__ssliCalls.push(['play', midi, dur, inst, vel]); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x91, 60, 1] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xD1, 96] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x81, 60, 0] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["startSustainedNote", 60, 96], calls)
        self.assertIn(["stopSustainedNote", 60], calls)
        self.assertNotIn(["play", 60, 1.6, 0, 1], calls)
        self.assertTrue(any(call[0] == "setExpression" and call[2] > 0.7 for call in calls))

    def test_regression_exquis_low_velocity_starts_audible_ssli_voice(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply(preset, inst) { window.__ssliCalls.push(['apply', preset.engine, preset.name, inst]); } },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ settings: { filter: {}, effects: {} } }]; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() {
                return {
                  getAvailableEffects() { return []; },
                  addToChain() {},
                  getEffect() { return { setEnabled() {}, setParam() {} }; },
                  setOrder() {},
                  setMasterMix() {}
                };
              },
              startSustainedNote(midi, velocity) {
                const normalized = velocity / 127;
                window.__ssliCalls.push(['startSustainedNote', midi, velocity, Number((normalized * normalized).toFixed(3))]);
              },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 1] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        starts = [call for call in calls if call[0] == "startSustainedNote"]
        self.assertEqual(len(starts), 1, calls)
        self.assertEqual(starts[0][1], 48, calls)
        self.assertGreaterEqual(starts[0][2], 48, calls)
        self.assertGreaterEqual(starts[0][3], 0.12, calls)

    def test_regression_exquis_raw_midi_is_not_octave_transposed(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ settings: { filter: {}, effects: {} } }]; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x9F, 48, 96] })")
        self.page.wait_for_function("() => document.querySelectorAll('.midi-held').length === 1")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["startSustainedNote", 48, 96], calls)
        self.assertIn("C3", self.page.locator('[data-testid="last-midi"]').inner_text())
        self.assertIn("raw=48", self.page.locator('[data-testid="diagnostic-log"]').inner_text())
        self.assertEqual(self.page.locator(".midi-held").get_attribute("data-cell-id"), "r5c3")

    def test_regression_midi_duplicate_note_highlights_centered_physical_cell(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x9F, 48, 96] })")
        self.page.wait_for_function("() => document.querySelectorAll('.midi-held').length === 1")
        held = self.page.locator(".midi-held")
        self.assertEqual(held.get_attribute("data-midi"), "48")
        self.assertEqual(held.get_attribute("data-cell-id"), "r5c3")
        self.assertNotEqual(held.get_attribute("data-cell-id"), "r4c0")

    def test_regression_repeated_exquis_notes_do_not_reapply_preset_or_leak_ssli_voices(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply(preset, inst) { window.__ssliCalls.push(['apply', preset.engine, preset.name, inst]); } },
            state: { notify(kind) { window.__ssliCalls.push(['notify', kind]); } },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained']); },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          for (let i = 0; i < 16; i += 1) {
            window.__mockExquisInput.onmidimessage({ data: [0x90 + i, 48 + i, 96] });
          }
        }
        """)
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual(len([call for call in calls if call[0] == "apply"]), 1, calls)
        self.assertEqual(len([call for call in calls if call[0] == "stopAllSustained"]), 1, calls)
        self.assertEqual(len([call for call in calls if call[0] == "startSustainedNote"]), 16, calls)
        self.assertGreaterEqual(len([call for call in calls if call[0] == "stopSustainedNote"]), 4, calls)
        self.assertLessEqual(self.page.locator(".midi-held").count(), 12)

    def test_regression_stale_note_off_after_prune_does_not_double_stop_or_clear_current_touch(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained']); },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          for (let i = 0; i < 13; i += 1) {
            window.__mockExquisInput.onmidimessage({ data: [0x90 + i, 48 + i, 96] });
          }
          window.__mockExquisInput.onmidimessage({ data: [0x80, 48, 0] });
        }
        """)
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual(len([call for call in calls if call[0] == "stopSustainedNote" and call[1] == 48]), 1, calls)
        self.assertEqual(self.page.locator(".midi-held").count(), 12)
        self.assertIn("note-off ignored stale C3", self.page.locator('[data-testid="diagnostic-log"]').inner_text())

    def test_regression_pressure_zero_for_one_held_note_does_not_collapse_expression_for_other_notes(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 96] });
          window.__mockExquisInput.onmidimessage({ data: [0x92, 52, 96] });
          window.__mockExquisInput.onmidimessage({ data: [0xD1, 0] });
        }
        """)
        calls = self.page.evaluate("() => window.__ssliCalls")
        expression_calls = [call for call in calls if call[0] == "setExpression"]
        self.assertGreaterEqual(len(expression_calls), 1, calls)
        self.assertEqual(expression_calls[-1], ["setExpression", 7779, 1.695], calls)
        self.assertFalse(any(call == ["clearExpression"] for call in calls), calls)

    def test_regression_play_mode_chords_keep_independent_ssli_voice_ownership(self):
        self.open_audio_drawer()
        self.page.locator('[data-testid="play-mode"]').click()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume() {},
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); activeOscs.set(midi, { midi }); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); activeOscs.delete(midi); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockChordInput = { id: 'play-chord-exquis', name: 'Play Chord Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockChordInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockChordInput && window.__mockChordInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockChordInput.onmidimessage({ data: [0x91, 48, 88] });
          window.__mockChordInput.onmidimessage({ data: [0x92, 52, 94] });
          window.__mockChordInput.onmidimessage({ data: [0x93, 55, 104] });
          window.__mockChordInput.onmidimessage({ data: [0x82, 52, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.some(call => call[0] === 'stopSustainedNote' && call[1] === 52)")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual([call[1] for call in calls if call[0] == "startSustainedNote"], [48, 52, 55], calls)
        self.assertEqual([call for call in calls if call[0] == "stopSustainedNote"], [["stopSustainedNote", 52]], calls)
        self.assertEqual(self.page.evaluate("() => [...window.SynthLab.audio.getActiveOscillators().keys()].sort((a, b) => a - b)"), [48, 55])
        self.assertEqual(self.page.locator(".midi-held").count(), 2)
        self.assertIn("Play mode: score paused", self.page.locator('[data-testid="drill-score"]').inner_text())
        self.assertNotIn("released duplicate MIDI voice", self.page.locator('[data-testid="diagnostic-log"]').inner_text())

    def test_regression_same_channel_buttons_keep_independent_held_voices(self):
        self.open_audio_drawer()
        self.page.locator('[data-testid="play-mode"]').click()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume() {},
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); activeOscs.set(midi, { midi }); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); activeOscs.delete(midi); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockSameChannelInput = { id: 'same-channel-exquis', name: 'Same Channel Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockSameChannelInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockSameChannelInput && window.__mockSameChannelInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockSameChannelInput.onmidimessage({ data: [0x90, 48, 96] });
          window.__mockSameChannelInput.onmidimessage({ data: [0x90, 52, 104] });
          window.__mockSameChannelInput.onmidimessage({ data: [0xA0, 48, 118] });
          window.__mockSameChannelInput.onmidimessage({ data: [0xA0, 52, 0] });
          window.__mockSameChannelInput.onmidimessage({ data: [0x80, 52, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.some(call => call[0] === 'stopSustainedNote' && call[1] === 52)")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual([call[1] for call in calls if call[0] == "startSustainedNote"], [48, 52], calls)
        self.assertEqual([call for call in calls if call[0] == "stopSustainedNote"], [["stopSustainedNote", 52]], calls)
        self.assertEqual(self.page.evaluate("() => [...window.SynthLab.audio.getActiveOscillators().keys()]"), [48])
        snapshot = self.page.evaluate("() => window.__exquisDebugSnapshot()")
        self.assertEqual(snapshot["heldNotes"], 1, snapshot)
        self.assertEqual(snapshot["midiVoices"], 1, snapshot)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("poly-aftertouch C3 pressure=118", log)
        self.assertIn("poly-aftertouch E3 pressure=0", log)
        self.assertNotIn("released previous channel voice", log)

    def test_regression_single_note_pressure_zero_does_not_fall_back_to_velocity(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 97] });
          window.__mockExquisInput.onmidimessage({ data: [0xD1, 0] });
        }
        """)
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["clearExpression"], calls)
        self.assertEqual(len([call for call in calls if call[0] == "setExpression" and call[1] == 7850]), 1, calls)
        self.assertGreater(calls.index(["clearExpression"]), 1, calls)
        self.assertIn("channel-pressure C3 pressure=0", self.page.locator('[data-testid="diagnostic-log"]').inner_text())

    def test_regression_pressure_flood_is_coalesced_before_ssli_expression(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x92, 47, 123] });
          window.__mockExquisInput.onmidimessage({ data: [0x9A, 53, 105] });
          for (const value of [123, 122, 123, 122, 124, 123, 124, 123, 122, 121, 120]) {
            window.__mockExquisInput.onmidimessage({ data: [0xD2, value] });
          }
          for (const value of [105, 104, 103, 102, 103, 102, 101, 102, 103, 104, 105]) {
            window.__mockExquisInput.onmidimessage({ data: [0xDA, value] });
          }
        }
        """)
        calls = self.page.evaluate("() => window.__ssliCalls")
        expression_calls = [call for call in calls if call[0] == "setExpression"]
        self.assertLessEqual(len(expression_calls), 8, calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI expression skipped", log)

    def test_regression_play_mode_pressure_changes_actual_subtractive_audio(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_subtractive_pressure_sweep"
        result = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--engine",
                "Subtractive",
                "--category",
                "Leads",
                "--preset-contains",
                "Saw Lead",
                "--trigger",
                "pressure-sweep-midi",
                "--normalization-midi",
                "48",
                "--audio-sample-ms",
                "900",
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        row = next(item for item in payload["results"] if item["presetLabel"] == "Saw Lead")
        signature = row["audioSignature"]
        self.assertEqual(result.returncode, 0, f"row={json.dumps(row, indent=2)}\nstdout={result.stdout}\nstderr={result.stderr}")
        self.assertGreater(float(signature["lowRms"]), 0.002, row)
        self.assertGreater(float(signature["rmsRatio"]), 1.18, row)
        self.assertGreater(float(signature["centroidRatio"]), 1.05, row)
        self.assertIn("SSLI expression pressure=120", signature["diagnosticLog"])

    def test_regression_play_mode_pressure_reaches_actual_physical_runtime(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_physical_pressure_sweep"
        result = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--engine",
                "Physical",
                "--category",
                "Bowed",
                "--preset-contains",
                "Cello Sul Tasto",
                "--trigger",
                "pressure-sweep-midi",
                "--normalization-midi",
                "48",
                "--audio-sample-ms",
                "900",
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=120,
        )
        payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        row = next(item for item in payload["results"] if item["presetLabel"] == "Cello Sul Tasto")
        signature = row["audioSignature"]
        self.assertEqual(result.returncode, 0, f"row={json.dumps(row, indent=2)}\nstdout={result.stdout}\nstderr={result.stderr}")
        response = max(
            float(signature["rmsRatio"]),
            1 / max(0.001, float(signature["rmsRatio"])),
            float(signature["centroidRatio"]),
            1 / max(0.001, float(signature["centroidRatio"])),
        )
        self.assertGreater(response, 1.25, row)
        self.assertIn("SSLI physical per-note pressure updated C3 pressure=120", signature["diagnosticLog"])

    def test_regression_ssli_midi_sustain_uses_performance_volume(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const instruments = [{ type: 'subtractive', settings: { volume: 42, filter: {}, effects: {} }, masterOutput: { gain: { value: 1 } } }];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return instruments; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume(inst, value) { instruments[inst].settings.volume = value; window.__ssliCalls.push(['setInstrumentVolume', inst, value]); },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity, instruments[0].settings.volume, instruments[0].masterOutput.gain.value]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 97] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["setInstrumentVolume", 0, 80], calls)
        self.assertTrue(any(call[0] == "startSustainedNote" and call[1] == 48 and call[2] == 97 and call[3] == 80 and call[4] == 1 for call in calls), calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI instrument inst=0 type=subtractive volume=42->80", log)
        self.assertNotIn("SSLI normalization preset=subtractive::Wurlitzer EP", log)

    def test_regression_ssli_celesta_does_not_use_output_boost_compensation(self):
        self.open_audio_drawer()
        celesta_value = self.page.locator('[data-testid="sound-preset-select"]').evaluate(
            """select => [...select.options].find((option) => option.textContent.trim() === 'Celesta').value"""
        )
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const instruments = [{ type: 'subtractive', settings: { volume: 42, filter: {}, effects: {} }, masterOutput: { gain: { value: 1 } } }];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return instruments; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume(inst, value) { instruments[inst].settings.volume = value; window.__ssliCalls.push(['setInstrumentVolume', inst, value]); },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity, instruments[0].settings.volume, instruments[0].masterOutput.gain.value]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="sound-preset-select"]').select_option(celesta_value)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 96] })")
        self.page.wait_for_function("() => window.__ssliCalls.some((call) => call[0] === 'startSustainedNote')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["setInstrumentVolume", 0, 80], calls)
        self.assertTrue(any(call[0] == "startSustainedNote" and call[1] == 48 and call[2] == 96 and call[3] == 80 and call[4] == 1 for call in calls), calls)
        self.page.wait_for_timeout(80)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertNotIn("SSLI normalization output preset=" + celesta_value, log)
        self.assertNotIn("SSLI normalization preset=" + celesta_value, log)

    def test_regression_ssli_rhodes_does_not_use_output_boost_compensation(self):
        self.open_audio_drawer()
        rhodes_value = self.page.locator('[data-testid="sound-preset-select"]').evaluate(
            """select => [...select.options].find((option) => option.textContent.trim() === 'Electric Piano (Rhodes)').value"""
        )
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const instruments = [{ type: 'subtractive', settings: { volume: 42, filter: {}, effects: {} }, masterOutput: { gain: { value: 1 } } }];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return instruments; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume(inst, value) { instruments[inst].settings.volume = value; window.__ssliCalls.push(['setInstrumentVolume', inst, value]); },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity, instruments[0].settings.volume, instruments[0].masterOutput.gain.value]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="sound-preset-select"]').select_option(rhodes_value)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 96] })")
        self.page.wait_for_function("() => window.__ssliCalls.some((call) => call[0] === 'startSustainedNote')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["setInstrumentVolume", 0, 80], calls)
        self.assertTrue(any(call[0] == "startSustainedNote" and call[1] == 48 and call[2] == 96 and call[3] == 80 and call[4] == 1 for call in calls), calls)
        self.page.wait_for_timeout(80)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertNotIn("SSLI normalization output preset=" + rhodes_value, log)

    def test_regression_exquis_midi_uses_linear_velocity_and_live_pressure_expression(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ type: 'subtractive', settings: { volume: 100, filter: {}, effects: {} } }]; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x96, 48, 101] });
          window.__mockExquisInput.onmidimessage({ data: [0xD6, 127] });
        }
        """)
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["startSustainedNote", 48, 101], calls)
        expression_calls = [call for call in calls if call[0] == "setExpression"]
        self.assertGreaterEqual(len(expression_calls), 1, calls)
        self.assertIn(["setExpression", 10000, 2], expression_calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("pressure=101", log)
        self.assertIn("SSLI expression pressure=127", log)

    def test_regression_fm_midi_translates_exquis_pressure_without_global_expression(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ type: 'fm', settings: { volume: 100, filter: {}, effects: {} } }]; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() {}
            },
            fm: {
              noteOn(midi, velocity, inst) { window.__ssliCalls.push(['fmNoteOn', midi, velocity, inst]); },
              noteOff(midi, inst) { window.__ssliCalls.push(['fmNoteOff', midi, inst]); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x96, 48, 48] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x96, 50, 64] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x96, 52, 127] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["fmNoteOn", 48, 78, 0], calls)
        self.assertIn(["fmNoteOn", 50, 90, 0], calls)
        self.assertIn(["fmNoteOn", 52, 127, 0], calls)
        self.assertFalse(any(call[0] == "startSustainedNote" for call in calls), calls)
        self.assertFalse(any(call[0] == "setExpression" for call in calls), calls)

    def test_regression_low_register_subtractive_poly_preserves_volume(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const lowRegisterSettings = {
            volume: 55,
            osc: [
              { wave: 'sawtooth', oct: -2, level: 70 },
              { wave: 'sawtooth', oct: -2, level: 70 },
              { wave: 'sine', oct: 0, level: 0 }
            ],
            filter: { enabled: true, type: 'lowpass', freq: 180, q: 25 },
            noise: { level: 0 },
            effects: {}
          };
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ type: 'subtractive', settings: lowRegisterSettings }]; },
              setInstrumentVolume(inst, volume) { window.__ssliCalls.push(['setInstrumentVolume', inst, volume]); lowRegisterSettings.volume = volume; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              getFinalDestination() { return { name: 'originalDestination' }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          [48, 50, 52, 53, 55, 57].forEach((midi, idx) => {
            window.__mockExquisInput.onmidimessage({ data: [0x90 | idx, midi, 112] });
          });
        }
        """)
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual([call[1] for call in calls if call[0] == "startSustainedNote"], [48, 50, 52, 53, 55, 57], calls)
        self.assertIn(["setInstrumentVolume", 0, 80], calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI MIDI sustain start A3 velocity=112 pressure=112 preset=subtractive::Wurlitzer EP", log)
        self.assertNotIn("boost=", log)

    def test_regression_ssli_midi_sustain_does_not_wrap_runtime_output(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const originalDestination = { name: 'originalDestination' };
          const instruments = [{ type: 'subtractive', settings: { volume: 100, filter: {}, effects: {} } }];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running', createGain() { window.__ssliCalls.push(['createGain']); throw new Error('unexpected output wrapper'); } }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return instruments; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              getFinalDestination() { window.__ssliCalls.push(['getFinalDestinationOriginal']); return originalDestination; },
              startSustainedNote(midi, velocity) {
                const destination = window.SynthLab.audio.getFinalDestination();
                window.__ssliCalls.push(['startSustainedNote', midi, velocity, destination.name, destination.gain && destination.gain.value]);
              },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x96, 48, 110] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertNotIn(["createGain"], calls)
        self.assertIn(["startSustainedNote", 48, 118, "originalDestination", None], calls)
        master_output = self.page.evaluate("() => window.SynthLab.audio.getInstruments()[0].masterOutput && window.SynthLab.audio.getInstruments()[0].masterOutput.name")
        self.assertIsNone(master_output)
        self.assertNotIn("SSLI output boost", self.page.locator('[data-testid="diagnostic-log"]').inner_text())

    def test_regression_exquis_soft_touch_expression_is_audible(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ settings: { filter: {}, effects: {} } }]; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote() {},
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x92, 48, 1] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["startSustainedNote", 48, 11], calls)
        self.assertFalse(any(call[0] == "setExpression" for call in calls), calls)

    def test_regression_live_pressure_caps_expression_gain_during_repeated_play(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ type: 'subtractive', settings: { volume: 100, filter: {}, effects: {} } }]; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained']); activeOscs.clear(); },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume(inst, volume) { window.__ssliCalls.push(['setInstrumentVolume', inst, volume]); },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); activeOscs.set(midi, { midi }); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); activeOscs.delete(midi); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="play-mode"]').click()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          const seq = [
            [0x90 | 2, 48, 7], [0xD0 | 2, 103],
            [0x90 | 9, 50, 7], [0xD0 | 9, 100],
            [0x80 | 2, 48, 0], [0x90 | 13, 53, 1], [0xD0 | 13, 101],
            [0x80 | 9, 50, 0], [0x80 | 13, 53, 0]
          ];
          seq.forEach(data => window.__mockExquisInput.onmidimessage({ data }));
        }
        """)
        calls = self.page.evaluate("() => window.__ssliCalls")
        expression_calls = [call for call in calls if call[0] == "setExpression"]
        self.assertGreaterEqual(len(expression_calls), 2, calls)
        self.assertTrue(all(call[2] <= 2 for call in expression_calls), calls)
        self.assertTrue(any(call[1] >= 8000 for call in expression_calls), calls)

    def test_regression_staggered_physical_plucked_chords_keep_chord_headroom(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="play-mode"]').click()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          const input = window.__mockExquisInput;
          const events = [
            [0, [0x9C, 47, 21]], [8, [0xDC, 76]],
            [90, [0x9B, 50, 1]], [98, [0xDB, 73]],
            [160, [0x8C, 47, 0]],
            [185, [0x98, 53, 1]], [193, [0xD8, 75]],
            [285, [0x8B, 50, 0]],
            [320, [0x88, 53, 0]]
          ];
          events.forEach(([delay, data]) => setTimeout(() => input.onmidimessage({ data }), delay));
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 3")
        self.page.wait_for_timeout(520)
        metrics = self.page.evaluate("""
        () => ({
          starts: window.__ssliCalls.filter(call => call[0] === 'physical.noteOn'),
          physicalOff: window.__ssliCalls.filter(call => call[0] === 'physical.noteOff'),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual([call[1] for call in metrics["starts"]], [47, 50, 53], metrics)
        self.assertEqual(metrics["physicalOff"], [], metrics)
        self.assertIn("SSLI plucked one-shot D3 velocity=32 pressure=1 decay=natural preset=physical::Nylon Guitar", metrics["log"])
        self.assertIn("SSLI plucked one-shot natural decay B2", metrics["log"])
        self.assertNotIn("SSLI engine all-notes-off after MIDI idle", metrics["log"])
        self.assertNotIn("boost=", metrics["log"])

    def test_regression_repeated_exquis_chords_do_not_accumulate_playback_latency(self):
        from tools.preset_signature_check import start_server

        server, url = start_server()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.page.goto(url)
        self.page.wait_for_selector('[data-testid="sound-engine-select"]')
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__exquisLatencyProbe = { inputs: [], starts: [] };
          window.__latencyInput = { id: 'latency-exquis', name: 'Latency Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__latencyInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__latencyInput && window.__latencyInput.onmidimessage")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('SSLI runtime preset API ready')")
        self.page.locator('[data-testid="play-step"]').click()
        self.page.wait_for_function("() => /SSLI preset applied|SSLI MIDI sustain start/.test(document.querySelector('[data-testid=\"diagnostic-log\"]').textContent)")
        self.page.locator('[data-testid="reset-console"]').click()
        self.page.locator('[data-testid="play-mode"]').click()
        metrics = self.page.evaluate("""
        async () => {
          const input = window.__latencyInput;
          const notes = [53, 47, 50];
          const expected = [];
          let delay = 0;
          for (let chord = 0; chord < 28; chord += 1) {
            notes.forEach((midi, index) => {
              const channel = (chord * 3 + index) % 14;
              const onDelay = delay + index * 8;
              const offDelay = delay + 54 + index * 3;
              expected.push({ midi, at: onDelay });
              setTimeout(() => input.onmidimessage({ data: [0x90 | channel, midi, 70 + index * 8] }), onDelay);
              setTimeout(() => input.onmidimessage({ data: [0xD0 | channel, 90 + index * 5] }), onDelay + 12);
              setTimeout(() => input.onmidimessage({ data: [0xD0 | channel, 0] }), offDelay - 4);
              setTimeout(() => input.onmidimessage({ data: [0x80 | channel, midi, 0] }), offDelay);
            });
            delay += 78;
          }
          const start = performance.now();
          await new Promise(resolve => setTimeout(resolve, delay + 700));
          const log = document.querySelector('[data-testid="diagnostic-log"]').textContent;
          const probe = window.__exquisLatencyProbe;
          const starts = probe.starts.slice();
          const inputs = probe.inputs.slice();
          const latencies = starts.map((entry, index) => entry.at - inputs[index].at);
          const sorted = latencies.slice().sort((a, b) => a - b);
          const excessRuntimeLogs = (log.match(/SSLI runtime inst=/g) || []).length;
          const pressureLogs = (log.match(/channel-pressure/g) || []).length;
          return {
            starts: starts.length,
            inputs: inputs.length,
            maxLatency: Math.max(...latencies),
            p95Latency: sorted[Math.floor(sorted.length * 0.95)],
            finalLatency: latencies[latencies.length - 1],
            runtimeLogs: excessRuntimeLogs,
            pressureLogs,
            log
          };
        }
        """)
        self.assertEqual(metrics["starts"], 84, metrics)
        self.assertEqual(metrics["inputs"], 84, metrics)
        self.assertLess(metrics["p95Latency"], 85, metrics)
        self.assertLess(metrics["maxLatency"], 160, metrics)
        self.assertLess(metrics["finalLatency"], 120, metrics)
        self.assertLess(metrics["runtimeLogs"], 8, metrics)
        self.assertLess(metrics["pressureLogs"], 80, metrics)
        self.assertNotIn("preset apply failed", metrics["log"])
        self.assertNotIn("SSLI MIDI unavailable", metrics["log"])
        self.assertNotIn("SSLI expression pressure=", metrics["log"])
        # Browser timer jitter in headless mode is not an audio latency oracle, but
        # this regression catches the main-thread backlog pattern that caused delay.

    def test_regression_diagnostic_logging_is_batched_off_hot_path(self):
        metrics = self.page.evaluate("""
        () => {
          const log = document.querySelector('[data-testid="diagnostic-log"]');
          const beforeText = log.textContent;
          const t0 = performance.now();
          for (let i = 0; i < 80; i += 1) {
            window.__exquisDebugLog('test', 'burst ' + i);
          }
          const immediateText = log.textContent;
          return new Promise(resolve => setTimeout(() => {
            resolve({
              elapsed: performance.now() - t0,
              beforeText,
              immediateText,
              afterText: log.textContent
            });
          }, 80));
        }
        """)
        self.assertEqual(metrics["immediateText"], metrics["beforeText"], metrics)
        self.assertIn("burst 79", metrics["afterText"], metrics)
        self.assertLess(metrics["elapsed"], 140, metrics)

    def test_regression_mpe_channel_reuse_releases_previous_voice(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ settings: { filter: {}, effects: {} } }]; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x92, 60, 96] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x92, 64, 96] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["startSustainedNote", 60, 96], calls)
        self.assertIn(["stopSustainedNote", 60], calls)
        self.assertIn(["startSustainedNote", 64, 127], calls)
        self.assertIn("released previous channel voice C4", self.page.locator('[data-testid="diagnostic-log"]').inner_text())

    def test_regression_mpe_same_note_on_new_channel_releases_previous_ssli_owner(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume() {},
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); activeOscs.set(midi, { midi }); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); activeOscs.delete(midi); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 2, 48, 80] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 9, 48, 95] })")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual(len([call for call in calls if call[0] == "startSustainedNote" and call[1] == 48]), 2, calls)
        self.assertEqual(len([call for call in calls if call == ["stopSustainedNote", 48]]), 1, calls)
        self.assertEqual(self.page.locator(".midi-held").count(), 1)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("released duplicate MIDI voice C3", log)
        self.assertIn("MIDI voices after-start C3 held=1 local=1 ssli=1", log)

    def test_regression_exquis_channel_16_note_events_are_playable_mpe_notes(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume() {},
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression() {},
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 3, 50, 95] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 5, 53, 58] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 15, 47, 112] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xB0 | 15, 74, 64] })")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('Exquis ch16 control id=74')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["startSustainedNote", 50, 110], calls)
        self.assertIn(["startSustainedNote", 53, 86], calls)
        self.assertIn(["startSustainedNote", 47, 119], calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("Exquis ch16 control id=74 value=64", log)
        self.assertIn("note-on B2", log)
        held_midis = self.page.locator(".midi-held").evaluate_all("els => els.map((el) => Number(el.dataset.midi)).sort((a, b) => a - b)")
        self.assertEqual(held_midis, [47, 50, 53])

    def test_regression_low_velocity_release_bounce_does_not_retrigger_note(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume() {},
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression() {},
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 4, 53, 21] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x80 | 4, 53, 0] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 6, 53, 1] })")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('note-on ignored release bounce F3')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual(len([call for call in calls if call[0] == "startSustainedNote" and call[1] == 53]), 1, calls)
        self.page.wait_for_function("() => window.__ssliCalls.some((call) => call[0] === 'stopSustainedNote' && call[1] === 53)")
        self.assertEqual(self.page.locator(".midi-held").count(), 0)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("note-on ignored release bounce F3 midi=53 raw=53 velocity=1 channel=7", log)

    def test_regression_low_velocity_retrigger_during_short_hold_does_not_double_start_voice(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume() {},
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression() {},
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 14, 53, 75] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x80 | 14, 53, 0] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 3, 53, 11] })")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('note-on ignored release bounce F3 midi=53 raw=53 velocity=11 channel=4')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual(len([call for call in calls if call[0] == "startSustainedNote" and call[1] == 53]), 1, calls)
        self.page.wait_for_function("() => window.__ssliCalls.some((call) => call[0] === 'stopSustainedNote' && call[1] === 53)")

    def test_regression_immediate_note_off_is_delayed_to_preserve_chord_member(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              stopAllSustained() {},
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume() {},
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity, performance.now()]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi, performance.now()]); },
              setExpression() {},
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 2, 53, 38] })")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x80 | 2, 53, 0] })")
        calls_before_delay = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["startSustainedNote", 53, 69], [call[:3] for call in calls_before_delay])
        self.assertFalse(any(call[0] == "stopSustainedNote" and call[1] == 53 for call in calls_before_delay), calls_before_delay)
        self.page.wait_for_function("() => window.__ssliCalls.some((call) => call[0] === 'stopSustainedNote' && call[1] === 53)")
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("note-off delayed short hold F3 midi=53 raw=53 channel=3", log)

    def test_regression_midi_note_on_color_is_distinct_from_root_white(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getCurrentInstrument() { return 0; },
              getInstruments() { return [{ type: 'subtractive', settings: { filter: {}, effects: {} } }]; },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression() {},
              clearExpression() {}
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="play-mode"]').click()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        root_color = self.page.locator(".key.tonic").first.evaluate("el => getComputedStyle(el).backgroundColor")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90, 48, 110] })")
        self.page.wait_for_timeout(50)
        metrics = self.page.locator(".key.midi-held").first.evaluate("""(el) => {
          const style = getComputedStyle(el);
          const nums = style.backgroundColor.match(/\\d+(?:\\.\\d+)?/g).map(Number);
          const scale = Math.max(...nums.slice(0, 3)) <= 1 ? 255 : 1;
          return {
            color: style.backgroundColor,
            outline: style.outlineColor,
            red: nums[0] * scale,
            green: nums[1] * scale,
            blue: nums[2] * scale
          };
        }""")
        self.assertNotEqual(metrics["color"], root_color)
        self.assertGreater(metrics["blue"], metrics["red"] + 20, metrics)
        self.assertGreater(metrics["blue"], metrics["green"], metrics)
        self.assertIn("rgb", metrics["outline"])

    def test_regression_midi_voice_bursts_cleanup_all_ssli_sustained_voices_when_idle(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__ssliCalls = [];
          const activeOscs = new Map();
          const makeInst = () => ({ type: 'subtractive', settings: { volume: 100, filter: {}, effects: {} } });
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running', createGain() { return { name: 'gain', gain: { value: 1 }, connect() {} }; } }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [makeInst()]; },
              stopAllSustained() { window.__ssliCalls.push(['stopAllSustained', activeOscs.size]); activeOscs.clear(); },
              loadInstrumentSettings() {},
              refreshFilter() {},
              freqToSlider(v) { return v; },
              qToSlider(v) { return v; },
              setInstrumentVolume() {},
              getInstrumentChain() { return { getAvailableEffects() { return []; }, addToChain() {}, getEffect() { return null; }, setOrder() {}, setMasterMix() {} }; },
              startSustainedNote(midi, velocity) { window.__ssliCalls.push(['startSustainedNote', midi, velocity]); activeOscs.set(midi, { midi }); },
              stopSustainedNote(midi) { window.__ssliCalls.push(['stopSustainedNote', midi]); },
              setExpression(cutoffHz, gainLinear) { window.__ssliCalls.push(['setExpression', Math.round(cutoffHz), Number(gainLinear.toFixed(3))]); },
              clearExpression() { window.__ssliCalls.push(['clearExpression']); }
            }
          };
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        for raw, channel in [(48, 0), (52, 1), (55, 2)]:
            self.page.evaluate("(args) => window.__mockExquisInput.onmidimessage({ data: [0x90 | args.channel, args.raw, 70] })", {"raw": raw, "channel": channel})
        for raw, channel in [(52, 1), (55, 2), (48, 0)]:
            self.page.evaluate("(args) => window.__mockExquisInput.onmidimessage({ data: [0x80 | args.channel, args.raw, 0] })", {"raw": raw, "channel": channel})
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertIn(["stopAllSustained", 3], calls)
        self.assertEqual(self.page.evaluate("() => window.SynthLab.audio.getActiveOscillators().size"), 0)
        self.assertIn("SSLI all sustained voices cleared after MIDI idle", self.page.locator('[data-testid="diagnostic-log"]').inner_text())

    def test_regression_midi_diagnostics_console_is_visible(self):
        console = self.page.locator('[data-testid="console-panel"]')
        log = self.page.locator('[data-testid="diagnostic-log"]')
        self.assertTrue(console.is_visible())
        self.assertFalse(log.is_visible())
        self.page.locator('[data-testid="audio-diag"]').click()
        self.assertTrue(log.is_visible())
        self.assertGreaterEqual(log.bounding_box()["height"], 180)

    def test_regression_audio_diag_reports_ssli_voice_pool_health(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          const activeOscs = new Map([[48, { midi: 48 }], [53, { midi: 53 }]]);
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              _activeNodeCount: 7,
              getCtx() { return { state: 'running', currentTime: 12.345, baseLatency: 0.012 }; },
              getActiveOscillators() { return activeOscs; },
              getVoicePoolStats() { return { totalAllocated: 80, peakUsage: 9, steals: 2, created: 80, currentlyActive: 3, available: 71 }; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ type: 'subtractive', settings: { volume: 100, filter: {}, effects: {} } }]; }
            }
          };
        }
        """)
        self.page.locator('[data-testid="audio-diag"]').click()
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI health manual", log)
        self.assertIn("ctx=running", log)
        self.assertIn("activeOsc=2", log)
        self.assertIn("nodeCount=7", log)
        self.assertIn("poolActive=3", log)
        self.assertIn("poolAvail=71", log)
        self.assertIn("steals=2", log)
        self.assertIn("scopePeak=", log)

    def test_regression_console_actions_fit_on_one_row(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""
        () => {
          const ids = ['audio-diag', 'reset-console', 'copy-console', 'exit-console'];
          const rects = ids.map(id => document.querySelector(`[data-testid="${id}"]`).getBoundingClientRect());
          const panel = document.querySelector('[data-testid="console-panel"]').getBoundingClientRect();
          return {
            tops: rects.map(r => Math.round(r.top)),
            lefts: rects.map(r => Math.round(r.left)),
            panelWidth: panel.width,
            sideRight: document.querySelector('.side-panel').getBoundingClientRect().right,
            panelRight: panel.right,
            rowSpread: Math.max(...rects.map(r => r.top)) - Math.min(...rects.map(r => r.top))
          };
        }
        """)
        self.assertLessEqual(metrics["rowSpread"], 2, metrics)
        self.assertEqual(metrics["lefts"], sorted(metrics["lefts"]), metrics)
        self.assertGreaterEqual(metrics["panelWidth"], 200, metrics)
        self.assertLessEqual(metrics["panelRight"], metrics["sideRight"] + 1, metrics)

    def test_regression_ssli_preset_selectors_are_hierarchical(self):
        self.assertTrue(self.page.locator('[data-testid="sound-engine-select"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="sound-category-select"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="sound-preset-select"]').is_visible())
        self.page.select_option('[data-testid="sound-engine-select"]', "subtractive")
        self.page.select_option('[data-testid="sound-category-select"]', "Keys")
        self.assertIn("Wurlitzer EP", self.page.locator('[data-testid="sound-preset-select"]').inner_text())

    def test_regression_fx_chain_selectors_are_hierarchical(self):
        self.assertTrue(self.page.locator('[data-testid="fx-category-select"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="fx-preset-select"]').is_visible())
        self.page.select_option('[data-testid="fx-category-select"]', "Performance / Live")
        self.assertIn("Lead Solo", self.page.locator('[data-testid="fx-preset-select"]').inner_text())

    def test_regression_fx_controls_share_one_visual_row(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""() => {
          const category = document.querySelector('[data-testid="fx-category-select"]').getBoundingClientRect();
          const preset = document.querySelector('[data-testid="fx-preset-select"]').getBoundingClientRect();
          const row = document.querySelector('[data-testid="fx-control-row"]').getBoundingClientRect();
          return {
            categoryTop: category.top,
            presetTop: preset.top,
            categoryBottom: category.bottom,
            presetBottom: preset.bottom,
            rowHeight: row.height,
            gap: preset.left - category.right
          };
        }""")
        self.assertLessEqual(abs(metrics["categoryTop"] - metrics["presetTop"]), 2, metrics)
        self.assertLessEqual(abs(metrics["categoryBottom"] - metrics["presetBottom"]), 2, metrics)
        self.assertLess(metrics["rowHeight"], 48, metrics)
        self.assertGreater(metrics["gap"], 4, metrics)

    def test_ssli_preset_select_contains_multiple_vendor_families(self):
        self.open_audio_drawer()
        engine_text = self.page.locator('[data-testid="sound-engine-select"]').inner_text()
        self.assertIn("subtractive", engine_text)
        self.assertIn("fm", engine_text)
        self.assertIn("physical", engine_text)
        self.assertNotIn("wavetable-synth", engine_text)
        self.page.locator('[data-testid="show-all-engines"]').check()
        engine_text = self.page.locator('[data-testid="sound-engine-select"]').inner_text()
        self.assertIn("wavetable-synth", engine_text)
        self.page.select_option('[data-testid="sound-engine-select"]', "subtractive")
        self.page.select_option('[data-testid="sound-category-select"]', "Keys")
        self.assertIn("Wurlitzer EP", self.page.locator('[data-testid="sound-preset-select"]').inner_text())

    def test_fx_preset_rebuilds_effect_chain(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="fx-category-select"]', "Ambient / Atmospheric")
        self.page.select_option('[data-testid="fx-preset-select"]', "deep-space")
        self.page.locator('[data-testid="test-audio"]').click()
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('FX chain Deep Space')")
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("effects=reverb,delay", log)

    def test_filter_controls_update_audio_state(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="filter-type-select"]', "bandpass")
        self.page.locator('[data-testid="filter-cutoff"]').fill("6400")
        self.page.locator('[data-testid="filter-resonance"]').fill("9.5")
        self.page.locator('[data-testid="test-audio"]').click()
        self.assertEqual(self.page.locator('[data-testid="filter-type-select"]').input_value(), "bandpass")
        self.assertEqual(self.page.locator('[data-testid="filter-cutoff"]').input_value(), "6400")
        self.assertEqual(self.page.locator('[data-testid="filter-resonance"]').input_value(), "9.5")
        self.assertIn("6400 Hz", self.page.locator("#filterCutoffValue").inner_text())
        self.assertEqual(self.page.locator("#filterResonanceValue").inner_text(), "9.5")
        self.assertIn("filter type bandpass", self.page.locator('[data-testid="diagnostic-log"]').inner_text())

    def test_exquis_midi_uses_selected_ssli_preset(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "subtractive")
        self.page.select_option('[data-testid="sound-category-select"]', "Leads")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Square Lead")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 64] })")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('preset=subtractive::Square Lead')")

    def test_ui_key_uses_selected_ssli_preset_and_fx(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "subtractive")
        self.page.select_option('[data-testid="sound-category-select"]', "Keys")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Wurlitzer EP")
        self.page.select_option('[data-testid="fx-category-select"]', "Performance / Live")
        self.page.select_option('[data-testid="fx-preset-select"]', "stage-keys")
        key = self.page.locator('[data-testid="exquis-key"]').first
        box = key.bounding_box()
        self.page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        self.page.mouse.down()
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('preset=subtractive::Wurlitzer EP')")
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("FX chain Stage Keys", log)
        self.page.mouse.up()

    def test_console_reset_and_exit_controls(self):
        self.assertTrue(self.page.locator('[data-testid="console-panel"]').is_visible())
        self.assertEqual(self.page.locator('[data-testid="reset-console"]').count(), 1)
        self.assertEqual(self.page.locator('[data-testid="copy-console"]').count(), 1)
        self.assertEqual(self.page.locator('[data-testid="exit-console"]').count(), 1)
        self.assertEqual(self.page.locator('[data-testid="exit-console"]').inner_text(), "Collapse")
        self.assertFalse(self.page.locator('[data-testid="diagnostic-log"]').is_visible())
        self.page.locator('[data-testid="test-audio"]').click()
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('audio')")
        self.page.locator('[data-testid="audio-diag"]').click()
        expanded_height = self.page.locator('[data-testid="diagnostic-log"]').bounding_box()["height"]
        self.assertGreaterEqual(expanded_height, 180)
        self.page.locator('[data-testid="reset-console"]').click()
        self.assertIn("reset", self.page.locator('[data-testid="diagnostic-log"]').inner_text())
        self.page.locator('[data-testid="exit-console"]').click()
        self.assertTrue(self.page.locator('[data-testid="console-panel"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="diagnostic-log"]').is_visible())

    def test_mock_midi_input_picker_switches_inputs(self):
        self.page.evaluate("""
        () => {
          window.__mockMidiInputA = { id: 'generic', name: 'Generic MIDI', manufacturer: 'USB', onmidimessage: null };
          window.__mockMidiInputB = { id: 'exquis-mock', name: 'Exquis Mock', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => { cb(window.__mockMidiInputA); cb(window.__mockMidiInputB); } },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockMidiInputB && window.__mockMidiInputB.onmidimessage")
        self.assertFalse(self.page.locator('[data-testid="midi-input-select"]').is_visible())
        self.page.locator('[data-testid="midi-input-select"]').evaluate("""el => {
          el.value = 'generic';
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }""")
        self.page.wait_for_function("() => window.__mockMidiInputA && window.__mockMidiInputA.onmidimessage")
        self.assertIn("Generic MIDI", self.page.locator('[data-testid="midi-status"]').inner_text())

    def test_auto_advance_can_be_disabled(self):
        self.open_audio_drawer()
        self.assertTrue(self.page.locator('[data-testid="auto-advance"]').is_checked())
        self.page.locator('[data-testid="auto-advance"]').uncheck()
        before = self.page.locator('[data-testid="step-readout"]').inner_text()
        self.page.evaluate("""
        () => {
          window.__mockMidiInput = { id: 'exquis-mock', name: 'Exquis Mock', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockMidiInput) },
            outputs: { forEach: () => {} }
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockMidiInput && window.__mockMidiInput.onmidimessage")
        target_midi = self.page.locator(".key.current").get_attribute("data-midi")
        self.page.evaluate("(midi) => window.__mockMidiInput.onmidimessage({ data: [0x90, Number(midi), 100] })", target_midi)
        self.assertEqual(self.page.locator('[data-testid="step-readout"]').inner_text(), before)

    def test_mobile_view_still_renders_controls(self):
        self.page.set_viewport_size({"width": 390, "height": 820})
        self.assertTrue(self.page.locator('[data-testid="tonic-select"]').is_visible())
        self.assertEqual(self.page.locator('[data-testid="exquis-key"]').count(), 61)

    def test_orientation_switch_keeps_actual_key_count(self):
        first_top = self.page.locator('[data-testid="exquis-key"]').first.bounding_box()
        self.page.select_option('[data-testid="orientation-select"]', "vertical")
        second_top = self.page.locator('[data-testid="exquis-key"]').first.bounding_box()
        self.assertEqual(self.page.locator('[data-testid="exquis-key"]').count(), 61)
        self.assertNotEqual(round(first_top["x"]), round(second_top["x"]))

    def test_rotate_surface_changes_physical_layout(self):
        first_box = self.page.locator('[data-testid="keyboard"]').bounding_box()
        first_key = self.page.locator('[data-testid="exquis-key"]').first.bounding_box()
        self.page.locator('[data-testid="rotate-surface"]').click()
        second_box = self.page.locator('[data-testid="keyboard"]').bounding_box()
        second_key = self.page.locator('[data-testid="exquis-key"]').first.bounding_box()
        self.assertEqual(self.page.locator('[data-testid="exquis-key"]').count(), 61)
        self.assertIn("Rotate 0", self.page.locator('[data-testid="rotate-surface"]').inner_text())
        self.assertEqual(self.page.locator('[data-testid="keyboard"]').get_attribute("data-rotation"), "180")
        self.assertNotEqual((round(first_key["x"]), round(first_key["y"])), (round(second_key["x"]), round(second_key["y"])))

    def test_regression_exquis_key_spacing_matches_compact_physical_honeycomb(self):
        spacing = self.page.evaluate("""() => {
          const keys = [...document.querySelectorAll('[data-testid="exquis-key"]')].map((el) => ({
            id: el.dataset.cellId,
            box: el.getBoundingClientRect()
          }));
          const byId = Object.fromEntries(keys.map((key) => [key.id, key.box]));
          const keyBox = document.querySelector('[data-testid="exquis-key"]').getBoundingClientRect();
          const center = (box) => ({ x: (box.left + box.right) / 2, y: (box.top + box.bottom) / 2 });
          const dist = (a, b) => Math.hypot(center(a).x - center(b).x, center(a).y - center(b).y);
          const sameRow = dist(byId.r0c1, byId.r0c0);
          const rowStep = dist(byId.r1c0, byId.r0c0);
          const nextRowSameCol = dist(byId.r2c0, byId.r0c0);
          return {
            sameRowRatio: sameRow / keyBox.height,
            rowStepRatio: rowStep / keyBox.height,
            nextRowSameColRatio: nextRowSameCol / keyBox.height
          };
        }""")
        self.assertGreaterEqual(spacing["sameRowRatio"], 0.99)
        self.assertLessEqual(spacing["sameRowRatio"], 1.01)
        self.assertGreaterEqual(spacing["rowStepRatio"], 0.99)
        self.assertLessEqual(spacing["rowStepRatio"], 1.01)
        self.assertGreaterEqual(spacing["nextRowSameColRatio"], 1.72)
        self.assertLessEqual(spacing["nextRowSameColRatio"], 1.74)

    def test_regression_supported_rotations_preserve_hex_layout(self):
        measurements = []
        for expected_rotation, expected_label in [(0, "Rotate 180"), (180, "Rotate 0")]:
            metrics = self.page.evaluate("""() => {
              const keyboard = document.querySelector('[data-testid="keyboard"]');
              const kb = keyboard.getBoundingClientRect();
              const keys = [...document.querySelectorAll('[data-testid="exquis-key"]')].map((el) => ({
                id: el.dataset.cellId,
                box: el.getBoundingClientRect()
              }));
              const byId = Object.fromEntries(keys.map((key) => [key.id, key.box]));
              const keyBox = document.querySelector('[data-testid="exquis-key"]').getBoundingClientRect();
              const center = (box) => ({ x: (box.left + box.right) / 2, y: (box.top + box.bottom) / 2 });
              const dist = (a, b) => Math.hypot(center(a).x - center(b).x, center(a).y - center(b).y);
              const boxes = keys.map((key) => key.box);
              const field = {
                left: Math.min(...boxes.map((box) => box.left)),
                right: Math.max(...boxes.map((box) => box.right)),
                top: Math.min(...boxes.map((box) => box.top)),
                bottom: Math.max(...boxes.map((box) => box.bottom))
              };
              const sameRow = dist(byId.r0c1, byId.r0c0);
              const adjacentRow = dist(byId.r1c0, byId.r0c0);
              const twoRows = dist(byId.r2c0, byId.r0c0);
              return {
                rotation: Number(keyboard.dataset.rotation),
                sameRowRatio: sameRow / keyBox.height,
                adjacentRowRatio: adjacentRow / keyBox.height,
                twoRowsRatio: twoRows / keyBox.height,
                leftPad: field.left - kb.left,
                rightPad: kb.right - field.right,
                topPad: field.top - kb.top,
                bottomPad: kb.bottom - field.bottom,
                count: keys.length
              };
            }""")
            measurements.append(metrics)
            self.assertEqual(metrics["rotation"], expected_rotation)
            self.assertIn(expected_label, self.page.locator('[data-testid="rotate-surface"]').inner_text())
            self.assertEqual(metrics["count"], 61)
            self.assertGreaterEqual(metrics["sameRowRatio"], 0.99)
            self.assertLessEqual(metrics["sameRowRatio"], 1.01)
            self.assertGreaterEqual(metrics["adjacentRowRatio"], 0.99)
            self.assertLessEqual(metrics["adjacentRowRatio"], 1.01)
            self.assertGreaterEqual(metrics["twoRowsRatio"], 1.72)
            self.assertLessEqual(metrics["twoRowsRatio"], 1.74)
            self.assertLess(abs(metrics["leftPad"] - metrics["rightPad"]), 4, measurements)
            self.assertLess(abs(metrics["topPad"] - metrics["bottomPad"]), 4, measurements)
            if expected_rotation != 180:
                self.page.locator('[data-testid="rotate-surface"]').click()

    def test_regression_scale_leds_are_visible_in_horizontal_and_vertical(self):
        allowed_notes = {"C", "D", "E", "F", "G", "A", "B"}
        for orientation in ["horizontal", "vertical"]:
            self.page.select_option('[data-testid="orientation-select"]', orientation)
            for desired_rotation in ["180", "0"]:
                if self.page.locator('[data-testid="keyboard"]').get_attribute("data-rotation") != desired_rotation:
                    self.page.locator('[data-testid="rotate-surface"]').click()
                metrics = self.page.locator('[data-testid="keyboard"]').evaluate("""keyboard => {
                  return [...keyboard.querySelectorAll('[data-testid="exquis-key"].hardware-lit')].map((el) => {
                    const style = getComputedStyle(el);
                    return {
                      note: el.querySelector('.note').textContent.trim(),
                      opacity: Number(style.opacity),
                      dimmed: el.classList.contains('dimmed'),
                      classes: el.className
                    };
                  });
                }""")
                self.assertGreaterEqual(len(metrics), 18)
                for key in metrics:
                    self.assertIn(key["note"], allowed_notes, [orientation, desired_rotation, key])
                    self.assertGreaterEqual(key["opacity"], 0.85, [orientation, desired_rotation, key])
                    self.assertFalse(key["dimmed"], [orientation, desired_rotation, key])

    def test_regression_unsupported_rotation_buttons_are_not_exposed(self):
        seen = []
        for _ in range(4):
            label = self.page.locator('[data-testid="rotate-surface"]').inner_text()
            seen.append(label)
            self.page.locator('[data-testid="rotate-surface"]').click()
        self.assertEqual(set(seen), {"Rotate 180", "Rotate 0"})
        self.assertNotIn("Rotate 90", seen)
        self.assertNotIn("Rotate 270", seen)

    def test_regression_hex_field_matches_tall_exquis_silhouette(self):
        silhouette = self.page.evaluate("""() => {
          const keys = [...document.querySelectorAll('[data-testid="exquis-key"]')].map((el) => {
            const box = el.getBoundingClientRect();
            return { id: el.dataset.cellId, box };
          });
          const boxes = keys.map((key) => key.box);
          const field = {
            left: Math.min(...boxes.map((box) => box.left)),
            right: Math.max(...boxes.map((box) => box.right)),
            top: Math.min(...boxes.map((box) => box.top)),
            bottom: Math.max(...boxes.map((box) => box.bottom))
          };
          const byId = Object.fromEntries(keys.map((key) => [key.id, key.box]));
          const keyBox = document.querySelector('[data-testid="exquis-key"]').getBoundingClientRect();
          const rowBounds = (prefix) => {
            const rowBoxes = keys.filter((key) => key.id.startsWith(prefix)).map((key) => key.box);
            const left = Math.min(...rowBoxes.map((box) => box.left));
            const right = Math.max(...rowBoxes.map((box) => box.right));
          const top = Math.min(...rowBoxes.map((box) => box.top));
          const bottom = Math.max(...rowBoxes.map((box) => box.bottom));
          const width = right - left;
          const height = bottom - top;
          return {
            left,
            right,
            top,
            bottom,
            width,
            height,
            major: Math.max(width, height),
            center: width >= height ? (left + right) / 2 : (top + bottom) / 2
          };
          };
          const row0 = rowBounds('r0c');
          const row1 = rowBounds('r1c');
          const width = field.right - field.left;
          const height = field.bottom - field.top;
          return {
            aspect: Math.max(width, height) / Math.min(width, height),
            rowWidthDeltaRatio: (row0.major - row1.major) / keyBox.height,
            rowCenterDelta: Math.abs(row0.center - row1.center)
          };
        }""")
        self.assertGreaterEqual(silhouette["aspect"], 1.62)
        self.assertLessEqual(silhouette["aspect"], 1.66)
        self.assertGreaterEqual(silhouette["rowWidthDeltaRatio"], 0.99)
        self.assertLessEqual(silhouette["rowWidthDeltaRatio"], 1.01)
        self.assertLessEqual(silhouette["rowCenterDelta"], 4)
    def test_desktop_layout_prioritizes_play_surface(self):
        self.page.set_viewport_size({"width": 1440, "height": 900})
        stage = self.page.locator(".stage-panel").bounding_box()
        side = self.page.locator(".side-panel").bounding_box()
        keyboard = self.page.locator('[data-testid="keyboard"]').bounding_box()
        top = self.page.locator('[data-testid="edge-top-controls"]').bounding_box()
        bottom = self.page.locator('[data-testid="edge-bottom-controls"]').bounding_box()
        device_width = max(top["x"] + top["width"], keyboard["x"] + keyboard["width"], bottom["x"] + bottom["width"]) - min(top["x"], keyboard["x"], bottom["x"])
        page_scroll_y = self.page.evaluate("() => document.documentElement.scrollHeight - document.documentElement.clientHeight")
        self.assertLess(stage["height"], 820)
        self.assertLessEqual(abs(stage["y"] - side["y"]), 2)
        self.assertGreater(device_width / stage["width"], 0.82)
        self.assertGreater(keyboard["height"], 330)
        self.assertLessEqual(page_scroll_y, 1)

    def test_regression_exquis_ui_is_visually_dominant(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        stage = self.page.locator(".stage-panel").bounding_box()
        keyboard = self.page.locator('[data-testid="keyboard"]').bounding_box()
        top = self.page.locator('[data-testid="edge-top-controls"]').bounding_box()
        bottom = self.page.locator('[data-testid="edge-bottom-controls"]').bounding_box()
        device_width = max(top["x"] + top["width"], keyboard["x"] + keyboard["width"], bottom["x"] + bottom["width"]) - min(top["x"], keyboard["x"], bottom["x"])
        self.assertGreaterEqual(device_width / stage["width"], 0.82)
        self.assertGreaterEqual(keyboard["height"], 315)

    def test_regression_keyboard_scales_to_available_stage_space(self):
        self.page.set_viewport_size({"width": 1600, "height": 900})
        self.page.wait_for_function("""() => {
          const stage = document.querySelector('.stage-panel').getBoundingClientRect();
          const header = document.querySelector('.stage-header').getBoundingClientRect();
          const top = document.querySelector('[data-testid="edge-top-controls"]').getBoundingClientRect();
          const keyboard = document.querySelector('[data-testid="keyboard"]').getBoundingClientRect();
          const bottom = document.querySelector('[data-testid="edge-bottom-controls"]').getBoundingClientRect();
          const availableWidth = stage.width - 20;
          const availableHeight = stage.bottom - header.bottom - 18;
          const device = {
            left: Math.min(top.left, keyboard.left, bottom.left),
            right: Math.max(top.right, keyboard.right, bottom.right),
            top: Math.min(top.top, keyboard.top, bottom.top),
            bottom: Math.max(top.bottom, keyboard.bottom, bottom.bottom)
          };
          return (device.right - device.left) / availableWidth >= 0.82 && (device.bottom - device.top) / availableHeight >= 0.62;
        }""")
        metrics = self.page.evaluate("""() => {
          const stage = document.querySelector('.stage-panel').getBoundingClientRect();
          const header = document.querySelector('.stage-header').getBoundingClientRect();
          const top = document.querySelector('[data-testid="edge-top-controls"]').getBoundingClientRect();
          const keyboard = document.querySelector('[data-testid="keyboard"]').getBoundingClientRect();
          const bottom = document.querySelector('[data-testid="edge-bottom-controls"]').getBoundingClientRect();
          const keys = [...document.querySelectorAll('[data-testid="exquis-key"]')].map((el) => el.getBoundingClientRect());
          const field = {
            left: Math.min(...keys.map((box) => box.left)),
            right: Math.max(...keys.map((box) => box.right)),
            top: Math.min(...keys.map((box) => box.top)),
            bottom: Math.max(...keys.map((box) => box.bottom))
          };
          const available = {
            width: stage.width - 20,
            height: stage.bottom - header.bottom - 18
          };
          const device = {
            left: Math.min(top.left, keyboard.left, bottom.left),
            right: Math.max(top.right, keyboard.right, bottom.right),
            top: Math.min(top.top, keyboard.top, bottom.top),
            bottom: Math.max(top.bottom, keyboard.bottom, bottom.bottom)
          };
          return {
            stage,
            top,
            keyboard,
            bottom,
            deviceWidth: device.right - device.left,
            deviceHeight: device.bottom - device.top,
            fieldWidth: field.right - field.left,
            fieldHeight: field.bottom - field.top,
            available,
            pageY: document.documentElement.scrollHeight - document.documentElement.clientHeight
          };
        }""")
        self.assertGreaterEqual(metrics["deviceWidth"] / metrics["available"]["width"], 0.82, metrics)
        self.assertGreaterEqual(metrics["deviceHeight"] / metrics["available"]["height"], 0.62, metrics)
        self.assertLess(metrics["bottom"]["right"], metrics["keyboard"]["left"], metrics)
        self.assertGreater(metrics["top"]["left"], metrics["keyboard"]["right"], metrics)
        self.assertGreaterEqual(metrics["fieldWidth"], 620, metrics)
        self.assertGreaterEqual(metrics["fieldHeight"], 360, metrics)
        self.assertLessEqual(metrics["pageY"], 1)

    def test_regression_guide_tone_is_separate_from_ssli_sound_controls(self):
        grouping = self.page.evaluate("""() => ({
          guideSection: document.querySelector('[data-testid="tone-select"]').closest('section').className,
          soundSection: document.querySelector('[data-testid="sound-engine-select"]').closest('section').className,
          sameSection: document.querySelector('[data-testid="tone-select"]').closest('section') === document.querySelector('[data-testid="sound-engine-select"]').closest('section')
        })""")
        self.assertEqual(grouping["guideSection"], "guide-section")
        self.assertEqual(grouping["soundSection"], "audio-section")
        self.assertFalse(grouping["sameSection"])

    def test_regression_no_scroll_layout_does_not_clip_right_rail(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""() => {
          const side = document.querySelector('.side-panel');
          return {
            pageX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
            pageY: document.documentElement.scrollHeight - document.documentElement.clientHeight,
            sideOverflow: side.scrollHeight - side.clientHeight,
            sideOverflowCss: getComputedStyle(side).overflow
          };
        }""")
        self.assertLessEqual(metrics["pageX"], 1)
        self.assertLessEqual(metrics["pageY"], 1)
        self.assertLessEqual(metrics["sideOverflow"], 1)
        self.assertNotEqual(metrics["sideOverflowCss"], "hidden")

    def test_regression_laptop_no_scroll_keeps_primary_controls_visible(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""() => {
          const selectors = [
            '[data-testid="orientation-select"]',
            '[data-testid="rotate-surface"]',
            '[data-testid="sound-engine-select"]',
            '[data-testid="sound-category-select"]',
            '[data-testid="sound-preset-select"]',
            '[data-testid="fx-category-select"]',
            '[data-testid="fx-preset-select"]',
            '[data-testid="filter-cutoff"]',
            '[data-testid="filter-resonance"]',
            '[data-testid="test-audio"]',
            '[data-testid="play-scale"]',
            '[data-testid="enable-midi"]'
          ];
          const viewport = { width: innerWidth, height: innerHeight };
          const boxes = selectors.map((selector) => {
            const el = document.querySelector(selector);
            const box = el.getBoundingClientRect();
            return { selector, top: box.top, bottom: box.bottom, left: box.left, right: box.right };
          });
          return {
            boxes,
            pageY: document.documentElement.scrollHeight - document.documentElement.clientHeight,
            belowViewport: boxes.filter((box) => box.bottom > viewport.height + 1).map((box) => box.selector),
            rightOfViewport: boxes.filter((box) => box.right > viewport.width + 1).map((box) => box.selector)
          };
        }""")
        self.assertLessEqual(metrics["pageY"], 1)
        self.assertEqual(metrics["belowViewport"], [])
        self.assertEqual(metrics["rightOfViewport"], [])

    def test_regression_enable_midi_is_first_prominent_side_rail_action(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""() => {
          const side = document.querySelector('.side-panel').getBoundingClientRect();
          const midiSection = document.querySelector('[data-testid="midi-coach-section"]');
          const guideSection = document.querySelector('.guide-section');
          const soundSection = document.querySelector('.audio-section');
          const drillSection = document.querySelector('[data-testid="drill-section"]');
          const enable = document.querySelector('[data-testid="enable-midi"]').getBoundingClientRect();
          const status = document.querySelector('[data-testid="midi-status"]').getBoundingClientRect();
          return {
            sideTop: side.top,
            midiSectionIndex: Array.from(document.querySelector('.side-panel').children).indexOf(midiSection),
            guideIndex: Array.from(document.querySelector('.side-panel').children).indexOf(guideSection),
            soundIndex: Array.from(document.querySelector('.side-panel').children).indexOf(soundSection),
            drillIndex: Array.from(document.querySelector('.side-panel').children).indexOf(drillSection),
            enableTop: enable.top,
            enableHeight: enable.height,
            statusTop: status.top,
            enableText: document.querySelector('[data-testid="enable-midi"]').textContent.trim()
          };
        }""")
        self.assertEqual(metrics["midiSectionIndex"], 0)
        self.assertLess(metrics["midiSectionIndex"], metrics["guideIndex"])
        self.assertLess(metrics["midiSectionIndex"], metrics["soundIndex"])
        self.assertLess(metrics["midiSectionIndex"], metrics["drillIndex"])
        self.assertLess(metrics["enableTop"] - metrics["sideTop"], 86)
        self.assertLess(metrics["statusTop"], metrics["enableTop"])
        self.assertGreaterEqual(metrics["enableHeight"], 44)
        self.assertIn("Enable MIDI", metrics["enableText"])

    def test_regression_midi_status_regions_remain_visible_and_live_on_laptop(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""() => {
          const selectors = [
            '[data-testid="midi-status"]',
            '[data-testid="midi-activity"]',
            '[data-testid="drill-score"]',
            '[data-testid="audio-status"]'
          ];
          return selectors.map((selector) => {
            const el = document.querySelector(selector);
            const box = el.getBoundingClientRect();
            return {
              selector,
              visible: getComputedStyle(el).display !== 'none' && box.width > 0 && box.height > 0,
              role: el.getAttribute('role'),
              live: el.getAttribute('aria-live')
            };
          });
        }""")
        for item in metrics:
            self.assertTrue(item["visible"], item)
            self.assertEqual(item["role"], "status", item)
            self.assertEqual(item["live"], "polite", item)

    def test_regression_keyboard_viewport_is_tight_around_physical_surface(self):
        keyboard = self.page.locator('[data-testid="keyboard"]').bounding_box()
        keys = self.page.locator('[data-testid="exquis-key"]').evaluate_all("""els => {
          const boxes = els.map((el) => el.getBoundingClientRect());
          return {
            left: Math.min(...boxes.map((box) => box.left)),
            right: Math.max(...boxes.map((box) => box.right)),
            top: Math.min(...boxes.map((box) => box.top)),
            bottom: Math.max(...boxes.map((box) => box.bottom))
          };
        }""")
        self.assertLessEqual((keyboard["width"] - (keys["right"] - keys["left"])) / (keys["right"] - keys["left"]), 0.28)
        self.assertLessEqual((keyboard["height"] - (keys["bottom"] - keys["top"])) / (keys["bottom"] - keys["top"]), 0.28)

    def test_regression_keyboard_surface_has_no_cartesian_background_grid(self):
        background = self.page.locator('[data-testid="keyboard"]').evaluate("el => getComputedStyle(el).backgroundImage")
        self.assertNotIn("linear-gradient", background)

    def test_regression_hex_field_is_centered_in_keyboard_viewport(self):
        metrics = self.page.locator('[data-testid="keyboard"]').evaluate("""keyboard => {
          const kb = keyboard.getBoundingClientRect();
          const boxes = [...keyboard.querySelectorAll('[data-testid="exquis-key"]')].map((el) => el.getBoundingClientRect());
          const keys = {
            left: Math.min(...boxes.map((box) => box.left)),
            right: Math.max(...boxes.map((box) => box.right)),
            top: Math.min(...boxes.map((box) => box.top)),
            bottom: Math.max(...boxes.map((box) => box.bottom))
          };
          return {
            leftPad: keys.left - kb.left,
            rightPad: kb.right - keys.right,
            topPad: keys.top - kb.top,
            bottomPad: kb.bottom - keys.bottom
          };
        }""")
        self.assertLess(abs(metrics["leftPad"] - metrics["rightPad"]), 28)
        self.assertLess(abs(metrics["topPad"] - metrics["bottomPad"]), 28)

    def test_medium_view_has_no_document_horizontal_overflow(self):
        self.page.set_viewport_size({"width": 1024, "height": 768})
        metrics = self.page.evaluate("""() => {
          const stage = document.querySelector('.stage-panel').getBoundingClientRect();
          const device = document.querySelector('[data-testid="exquis-device"]').getBoundingClientRect();
          return {
            stage,
            device,
            overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
            vertical: document.documentElement.scrollHeight - document.documentElement.clientHeight
          };
        }""")
        self.assertLessEqual(metrics["overflow"], 1, metrics)
        self.assertLessEqual(metrics["vertical"], 1, metrics)
        self.assertGreaterEqual(metrics["device"]["left"], metrics["stage"]["left"] + 4, metrics)
        self.assertLessEqual(metrics["device"]["right"], metrics["stage"]["right"] - 4, metrics)
        self.assertTrue(self.page.locator('[data-testid="keyboard"]').is_visible())

    def test_regression_tablet_horizontal_hardware_fits_stage(self):
        self.page.set_viewport_size({"width": 1024, "height": 768})
        self.page.select_option('[data-testid="orientation-select"]', "horizontal")
        self.page.wait_for_timeout(100)
        metrics = self.page.evaluate("""() => {
          const stage = document.querySelector('.stage-panel').getBoundingClientRect();
          const device = document.querySelector('[data-testid="exquis-device"]').getBoundingClientRect();
          const side = document.querySelector('.side-panel').getBoundingClientRect();
          return { stage, device, side };
        }""")
        self.assertGreaterEqual(metrics["device"]["left"], metrics["stage"]["left"] + 4, metrics)
        self.assertLessEqual(metrics["device"]["right"], metrics["stage"]["right"] - 4, metrics)
        self.assertGreater(metrics["side"]["top"], metrics["stage"]["bottom"] - 2, metrics)

    def test_mobile_surface_is_intentionally_pannable(self):
        self.page.set_viewport_size({"width": 390, "height": 844})
        overflow = self.page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
        self.assertLessEqual(overflow, 1)
        stage_scrollable = self.page.locator(".stage-panel").evaluate("el => el.scrollWidth > el.clientWidth")
        self.assertTrue(stage_scrollable)
        self.assertEqual(self.page.locator('[data-testid="exquis-key"]').count(), 61)

    def test_regression_mobile_build_badge_does_not_cover_playable_keys(self):
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.page.select_option('[data-testid="orientation-select"]', "vertical")
        self.page.wait_for_timeout(100)
        overlaps = self.page.evaluate("""() => {
          const badge = document.querySelector('[data-testid="build-version"]').getBoundingClientRect();
          return [...document.querySelectorAll('[data-testid="exquis-key"]')].filter((key) => {
            const box = key.getBoundingClientRect();
            return Math.max(badge.left, box.left) < Math.min(badge.right, box.right)
              && Math.max(badge.top, box.top) < Math.min(badge.bottom, box.bottom);
          }).map((key) => key.dataset.cellId);
        }""")
        self.assertEqual(overlaps, [])

    def test_practice_colors_and_key_affordance_are_distinct(self):
        tonic_bg = self.page.locator(".key.tonic").first.evaluate("el => getComputedStyle(el).backgroundColor")
        path_bg = self.page.locator(".key.in-path:not(.tonic)").first.evaluate("el => getComputedStyle(el).backgroundColor")
        self.page.select_option('[data-testid="view-select"]', "scale")
        scale_bg = self.page.locator(".key.in-scale:not(.tonic)").first.evaluate("el => getComputedStyle(el).backgroundColor")
        dimmed_opacity = float(self.page.locator(".key.dimmed").first.evaluate("el => getComputedStyle(el).opacity"))
        self.assertNotEqual(tonic_bg, path_bg)
        self.assertNotEqual(path_bg, scale_bg)
        self.assertGreaterEqual(dimmed_opacity, 0.4)
if __name__ == "__main__":
    unittest.main()
