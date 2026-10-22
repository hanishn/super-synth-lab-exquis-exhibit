import json
import subprocess
import unittest
from concurrent.futures import ThreadPoolExecutor
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
        "practice_coach_status_regions_must_remain_visible_on_laptop": "test_regression_practice_coach_status_regions_remain_visible_and_live_on_laptop",
        "fingering_root_must_not_be_overwritten": "test_regression_selected_root_keeps_first_fingering_assignment",
        "fingering_labels_must_stay_valid": "test_regression_fingering_labels_are_valid_for_visible_path",
        "wrist_led_pairs_must_allow_same_finger_for_nearby_steps": "test_regression_wrist_led_pairs_allow_same_finger_for_d3_e3",
        "natural_clusters_must_prioritize_human_finger_names": "test_regression_natural_clusters_prioritize_human_finger_names",
        "natural_clusters_must_be_default_fingering_strategy": "test_regression_natural_clusters_is_default_fingering_strategy",
        "scale_fingering_must_ascend_root_to_octave": "test_regression_scale_path_ascends_root_to_octave",
        "practice_octaves_must_match_physical_play_labels": "test_regression_practice_octaves_match_physical_play_labels",
        "duplicate_pitch_choices_must_prefer_centered_chain_cell": "test_regression_duplicate_pitch_choices_prefer_centered_chain_cell",
        "duplicate_pitch_lighting_must_choose_one_meridian_pad": "test_regression_c_minor_lights_only_the_meridian_duplicate_in_ui_and_hardware",
        "root_marker_must_not_depend_on_hue_alone": "test_regression_root_marker_is_visible_without_relying_on_hue",
        "reduced_motion_must_retain_target_emphasis": "test_regression_expressive_light_reduced_motion_keeps_static_target_emphasis",
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
        "practice_audio_must_not_expose_a_legacy_guide_tone_selector": "test_regression_practice_audio_has_no_legacy_guide_tone_selector",
        "exquis_ui_must_not_be_tiny": "test_regression_exquis_ui_is_visually_dominant",
        "ssli_presets_need_engine_category_preset_selectors": "test_regression_ssli_preset_selectors_are_hierarchical",
        "ssli_engine_dropdown_defaults_to_mature_engines": "test_regression_sound_engine_dropdown_defaults_to_mature_engines_with_show_all_opt_in",
        "fx_chains_need_category_preset_selectors": "test_regression_fx_chain_selectors_are_hierarchical",
        "fx_controls_must_share_one_visual_row": "test_regression_fx_controls_share_one_visual_row",
        "preset_changes_must_change_generated_sound": "test_regression_preset_changes_audio_graph_not_just_label",
        "filter_and_fx_chain_must_use_real_ssli_audio_api": "test_regression_filter_and_fx_controls_call_ssli_audio_api",
        "ssli_engines_must_initialize_before_selected_preset_playback": "test_regression_ssli_engine_initializes_before_selected_preset_playback",
        "exquis_midi_must_use_ssli_sustained_notes_and_expression": "test_regression_exquis_midi_uses_ssli_sustained_note_and_expression_api",
        "hardware_target_sync_must_clear_previous_pulses": "test_regression_exquis_sync_pulses_current_targets_and_clears_prior_targets",
        "hardware_target_pulse_must_advance_after_correct_midi_sequence_note": "test_regression_exquis_sync_advances_target_pulse_after_correct_sequence_note",
        "practice_notation_must_follow_canonical_target_step": "test_regression_practice_notation_lens_tracks_step_and_conceals_ear_answers",
        "hardware_chord_sync_must_pulse_all_current_targets": "test_regression_exquis_sync_pulses_every_current_chord_target",
        "rgb_probe_must_use_official_pad_only_protocol": "test_regression_exquis_rgb_pad_probe_uses_official_pad_only_direct_led_protocol",
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
        "practice_coach_must_be_first_prominent_side_rail_surface": "test_regression_practice_coach_is_first_prominent_side_rail_surface",
        "practice_coach_must_be_authoritative_learning_surface": "test_regression_practice_coach_is_the_authoritative_learning_surface",
        "practice_coach_outcome_must_name_next_action": "test_regression_practice_coach_outcome_names_the_next_action",
        "session_settings_must_use_a_specific_learner_facing_label": "test_regression_session_settings_uses_a_specific_learner_facing_label",
        "harmony_fixture_must_resolve_minor_first_inversion_to_exact_cells": "test_regression_harmony_fixture_resolves_minor_first_inversion_to_exact_cells",
        "harmony_fixtures_must_preserve_quality_through_inversions": "test_regression_harmony_fixtures_preserve_quality_through_inversions",
        "harmony_triad_lesson_must_expose_quality_and_inversion": "test_regression_harmony_triad_lesson_exposes_quality_and_inversion",
        "harmony_triad_must_score_an_inverted_minor_grip_once": "test_regression_harmony_triad_scores_an_inverted_minor_grip_once",
        "voice_leading_must_choose_common_tone_minimum_motion_destination": "test_regression_voice_leading_chooses_common_tone_minimum_motion_destination",
        "voice_leading_lesson_must_present_source_then_common_tone_destination": "test_regression_voice_leading_lesson_presents_source_then_common_tone_destination",
        "voice_leading_must_score_source_and_destination_grips_in_sequence": "test_regression_voice_leading_scores_source_and_destination_grips_in_sequence",
        "ear_to_gesture_must_conceal_exact_targets_and_preserve_score_when_prompting": "test_regression_ear_to_gesture_conceals_targets_and_prompt_playback_preserves_score",
        "ear_to_gesture_must_score_exact_interval_and_repair_wrong_interval": "test_regression_ear_to_gesture_scores_exact_interval_and_repairs_wrong_interval",
        "ear_to_gesture_interval_fixtures_must_keep_minor_and_major_prompts_exact": "test_regression_ear_to_gesture_interval_fixtures_keep_minor_and_major_prompts_exact",
        "ear_to_gesture_perfect_fifth_must_score_exact_grip": "test_regression_ear_to_gesture_perfect_fifth_scores_exact_grip",
        "progression_fixture_must_resolve_c_major_i_iv_v_i_to_exact_triads": "test_regression_progression_fixture_resolves_c_major_i_iv_v_i_to_exact_triads",
        "progression_lesson_must_present_i_iv_v_i_in_order": "test_regression_progression_lesson_presents_i_iv_v_i_in_order",
        "progression_lesson_must_retain_wrong_chord_and_advance_on_correct_chord": "test_regression_progression_lesson_retains_wrong_chord_and_advances_on_correct_chord",
        "progression_fixture_must_resolve_c_major_ii_v_i_to_exact_triads": "test_regression_progression_fixture_resolves_c_major_ii_v_i_to_exact_triads",
        "progression_lesson_must_present_ii_v_i_in_order": "test_regression_progression_lesson_presents_ii_v_i_in_order",
        "ii_v_i_fixture_must_transpose_functions_and_voicings_for_c_f_and_bb": "test_regression_ii_v_i_fixture_transposes_functions_and_voicings_for_c_f_and_bb",
        "ii_v_i_lesson_must_rebuild_from_selected_tonic": "test_regression_ii_v_i_lesson_rebuilds_from_the_selected_tonic",
        "f_major_resolution_must_use_compact_centerward_voicing": "test_regression_f_major_resolution_uses_the_compact_centerward_voicing",
        "dorian_vamp_must_transpose_and_resolve_as_playable_minor_to_major_pair": "test_regression_dorian_vamp_transposes_and_resolves_as_playable_minor_to_major_pair",
        "exercise_order_must_remain_stable_when_scale_changes": "test_regression_exercise_order_remains_stable_when_scale_changes",
        "exercise_chooser_must_use_explicit_families_without_scale_driven_reordering": "test_regression_exercise_chooser_uses_explicit_families_without_scale_driven_reordering",
        "progressions_must_open_with_a_major_starter_lesson": "test_regression_progressions_open_with_a_major_starter_lesson",
        "midi_must_be_the_hardware_first_launch_action": "test_regression_midi_is_the_hardware_first_launch_action",
        "exercise_chooser_controls_must_remain_readable_at_desktop_width": "test_regression_exercise_chooser_controls_remain_readable_at_desktop_width",
        "progression_library_must_offer_a_broad_transposable_curriculum": "test_regression_progression_library_offers_a_broad_transposable_curriculum",
        "ssli_genre_progression_library_must_remain_browsable_and_playable": "test_regression_ssli_genre_progression_library_remains_browsable_and_playable",
        "imported_progression_catalog_must_use_learner_facing_labels": "test_regression_imported_progression_catalog_uses_learner_facing_labels",
        "progressions_must_offer_global_and_per_chord_voicing_controls": "test_regression_progressions_offer_global_and_per_chord_voicing_controls",
        "chord_fingering_must_not_reuse_single_note_sequence_labels": "test_regression_chord_fingering_uses_distinct_labels_from_sequence_fingering",
        "exquis_chords_must_use_adjacent_finger_positions_not_piano_spacing": "test_regression_exquis_chord_fingers_follow_adjacent_button_order",
        "exquis_chord_fingers_must_use_contiguous_positions_for_every_voicing_size": "test_regression_exquis_chord_fingers_use_contiguous_span_for_every_voicing_size",
        "repertoire_lessons_must_use_named_loopable_sections_on_existing_progression_events": "test_regression_repertoire_lessons_expose_named_loopable_sections",
        "progression_library_templates_must_resolve_playable_chords_across_major_keys": "test_regression_progression_library_templates_resolve_playable_chords_across_major_keys",
        "progression_prompt_must_include_every_current_chord_member": "test_regression_progression_prompt_includes_every_current_chord_member",
        "exercise_control_must_not_overflow_header_at_desktop_viewport": "test_regression_exercise_control_does_not_overflow_header_at_desktop_viewport",
        "first_ssli_prompt_must_fall_back_until_preset_output_is_ready": "test_regression_first_ssli_prompt_falls_back_until_preset_output_is_ready",
        "first_fallback_note_must_wait_for_audio_context_resume": "test_regression_first_fallback_note_waits_for_audio_context_resume",
        "progression_current_chord_must_highlight_every_target_button": "test_regression_progression_current_chord_highlights_every_target_button",
        "expressive_light_frame_must_keep_root_relative_interval_identity": "test_regression_expressive_light_frame_is_root_relative_and_marks_every_chord_target",
        "expressive_light_targets_must_pulse_without_hiding_note_identity": "test_regression_expressive_light_targets_pulse_without_hiding_interval_identity",
        "illuminated_pad_labels_must_remain_legible": "test_regression_illuminated_pad_labels_have_minimum_contrast",
        "major_progression_must_replace_prior_minor_path_with_selected_key_lights": "test_regression_major_progression_replaces_minor_scale_path_with_current_chord_targets",
        "ipad_shell_must_prioritize_playing_canvas_over_setup_controls": "test_regression_ipad_shell_prioritizes_playing_canvas_over_setup_controls",
        "practice_surface_must_use_its_available_canvas": "test_regression_practice_surface_uses_its_available_canvas",
        "build_metadata_must_not_cover_the_practice_surface": "test_regression_build_metadata_does_not_dominate_practice_surface",
        "workspaces_must_separate_practice_library_and_studio": "test_regression_workspaces_separate_practice_library_and_studio",
        "midi_diagnostics_console_must_be_visible": "test_regression_midi_diagnostics_console_is_visible",
        "studio_diagnostics_must_open_a_visible_hardware_drawer": "test_regression_studio_diagnostics_opens_visible_hardware_drawer",
        "studio_hardware_must_fit_laptop_height_without_scroll_or_cutoff": "test_regression_studio_hardware_fits_laptop_height_without_scroll_or_cutoff",
        "exquis_sysex_helpers_must_encode_official_root_scale_messages": "test_regression_exquis_sysex_helpers_encode_official_root_scale_messages",
        "exquis_key_mode_sync_must_use_official_developer_sysex": "test_regression_exquis_key_mode_sync_uses_official_developer_sysex",
        "manual_key_mode_changes_must_beat_delayed_hardware_readbacks": "test_regression_manual_key_mode_change_syncs_after_hardware_readback",
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
        "midi_duplicate_note_highlight_must_illuminate_all_matching_physical_cells": "test_regression_midi_duplicate_note_illuminates_all_matching_physical_cells",
        "midi_duplicate_note_must_not_invent_a_physical_pad_identity": "test_regression_midi_duplicate_note_keeps_hardware_identity_ambiguous",
        "duplicate_pitch_hardware_evidence_must_score_the_guided_grip_without_inventing_pad_identity": "test_regression_grip_accepts_pitch_only_hardware_evidence_for_duplicate_target",
        "midi_note_on_must_be_blue_white_not_root_white": "test_regression_midi_note_on_color_is_distinct_from_root_white",
        "all_tonic_pitch_class_keys_must_be_root_white": "test_regression_all_c_keys_are_tonic_in_default_c_major",
        "horizontal_and_vertical_scale_leds_must_stay_visibly_lit": "test_regression_scale_leds_are_visible_in_horizontal_and_vertical",
        "horizontal_layout_must_rotate_physical_key_shapes": "test_regression_horizontal_layout_rotates_physical_key_shapes",
        "hexes_must_be_regular_and_share_edges": "test_regression_hexes_are_regular_and_share_edges",
        "keyboard_must_not_remain_tiny_when_stage_has_room": "test_regression_keyboard_scales_to_available_stage_space",
        "presets_must_not_play_default_sound": "test_regression_ssli_runtime_preset_changes_played_instrument",
        "preset_sweep_must_intone_distinct_real_engine_audio": "test_regression_preset_signature_check_intones_distinct_real_engines",
        "midi_preset_sweep_must_intone_selected_engine_audio": "test_regression_preset_signature_check_intones_physical_koto_through_midi",
        "mature_engine_categories_must_pass_six_note_poly_pressure_audio_sweep": "test_regression_preset_sweep_runs_mature_engine_category_continuous_poly_aftertouch_audio",
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
        "real_plucked_release_strum_press_must_not_trigger_audio": "test_regression_real_plucked_release_strum_press_has_no_audio_transient",
        "real_plucked_same_pitch_fast_repress_must_finger_mute_old_tail": "test_regression_real_plucked_same_pitch_fast_repress_finger_mutes_old_tail_without_new_pluck",
        "real_plucked_immediate_repress_must_not_emit_prior_release": "test_regression_real_plucked_immediate_repress_does_not_emit_prior_release",
        "real_plucked_release_pluck_must_start_on_note_up": "test_regression_real_plucked_release_pluck_starts_on_note_up_without_scheduled_attack",
        "plucked_exquis_low_velocity_pressure_spike_must_not_pluck": "test_regression_plucked_exquis_low_velocity_pressure_spike_contact_noise_does_not_pluck",
        "plucked_exquis_ambiguous_release_must_absorb_same_key_recontact": "test_regression_plucked_exquis_ambiguous_release_absorbs_immediate_same_key_recontact",
        "plucked_exquis_repeated_ambiguous_same_key_contacts_must_absorb": "test_regression_plucked_exquis_repeated_ambiguous_same_key_contacts_absorb_until_final_release",
        "three_note_plucked_strum_must_have_stable_audio_output": "test_regression_three_note_plucked_strum_has_stable_audio_output",
        "physical_poly_aftertouch_must_remain_per_note": "test_regression_four_note_physical_voices_track_pressure_independently_without_global_expression",
        "plucked_physical_pressure_must_be_forwarded_per_note_to_audio_engine": "test_regression_plucked_physical_pressure_is_forwarded_per_note_to_audio_engine",
        "six_note_physical_pressure_must_be_audio_tested": "test_regression_six_note_physical_pressure_flow_has_stable_final_audio_output",
        "six_note_physical_voices_must_keep_independent_pressure_updates": "test_regression_six_note_physical_voices_keep_independent_pressure_updates",
        "physical_pressure_stream_must_rate_limit_per_note_without_dropping_release": "test_regression_physical_pressure_stream_is_rate_limited_per_note_but_release_passes",
        "midi_preset_cache_must_verify_live_ssli_engine": "test_regression_midi_reapplies_preset_when_live_ssli_engine_does_not_match_cache",
        "midi_ssli_fallback_must_report_missing_runtime_api": "test_regression_midi_reports_missing_ssli_runtime_api_before_local_fallback",
        "ssli_preset_selection_must_retry_when_runtime_loads_late": "test_regression_preset_selection_retries_when_ssli_runtime_loads_late",
        "ssli_voice_pool_must_reclaim_available_voices_after_short_note_churn": "test_regression_ssli_voice_pool_reclaims_available_emergency_voices_after_short_note_churn",
        "ssli_pwm_lead_short_notes_must_track_every_sustained_start": "test_regression_ssli_start_sustained_tracks_every_pwm_lead_short_note",
        "hidden_ssli_iframe_must_reclaim_released_voices_without_animation_frames": "test_regression_hidden_ssli_iframe_reclaims_released_voices_without_animation_frames",
        "parent_must_reject_ssli_start_without_runtime_voice_ownership": "test_regression_parent_rejects_ssli_sustain_start_without_tracked_voice",
        "fm_dx_rhodes_must_not_be_noisy_poppy_or_bell_like": "test_regression_fm_dx_rhodes_uat_audio_acceptance",
        "uat_quiet_spot_presets_must_clear_single_note_floor": "test_regression_uat_quiet_spot_presets_clear_single_note_floor",
        "physical_marimba_c3_must_not_be_blown_out_relative_to_c4": "test_regression_physical_marimba_c3_is_balanced_against_c4",
        "uat_spot_presets_must_not_require_hard_velocity_for_loudness": "test_regression_uat_spot_presets_have_medium_velocity_loudness",
        "uat_fm_spot_presets_must_not_collapse_to_same_timbre": "test_regression_uat_fm_spot_presets_do_not_collapse_to_same_timbre",
        "embedded_ssli_iframe_must_not_bind_web_midi_directly": "test_regression_embedded_ssli_iframe_does_not_bind_web_midi_directly",
        "fm_dx_rhodes_normal_pressure_must_remain_playable": "test_regression_fm_dx_rhodes_normal_pressure_is_playable",
        "low_velocity_aftertouch_must_lift_subtractive_audio": "test_regression_low_velocity_aftertouch_lifts_actual_subtractive_audio",
        "midi_coach_activity_must_list_currently_held_notes": "test_regression_midi_coach_activity_lists_all_currently_held_notes",
        "physical_nylon_guitar_must_not_sound_like_sustained_pad": "test_regression_physical_nylon_guitar_does_not_ring_like_sustained_pad",
        "plucked_duplicate_channel_press_must_not_fire_old_pending_release": "test_regression_plucked_duplicate_channel_press_does_not_fire_old_pending_release",
        "plucked_contact_noise_must_not_become_note_attack": "test_regression_plucked_ignores_velocity_one_contact_noise_while_held",
        "plucked_interaction_must_not_apply_low_velocity_pressure_swell": "test_regression_plucked_interaction_does_not_apply_low_velocity_pressure_swell",
        "plucked_low_velocity_release_must_still_pluck": "test_regression_plucked_low_velocity_real_pressure_release_still_plucks",
        "plucked_presets_must_trigger_on_note_up": "test_regression_plucked_presets_trigger_on_note_up_not_note_down",
        "plucked_short_release_must_commit_before_next_press": "test_regression_plucked_short_release_fires_before_next_different_press",
        "preset_sweep_voice_stress_must_remain_stable": "test_regression_preset_sweep_runs_mature_engine_category_200_note_voice_stress_audio",
        "recontact_must_damp_committed_plucked_tail": "test_regression_real_plucked_same_key_recontact_damps_committed_release_tail",
        "repeated_plucked_pressure_must_not_use_live_swell": "test_regression_repeated_plucked_pressure_never_enters_live_swell_path",
        "ssli_voice_steal_cleanup_must_not_free_reused_voice": "test_regression_ssli_voice_steal_cleanup_does_not_free_reused_voice",
        "struck_interaction_must_not_apply_low_velocity_pressure_swell": "test_regression_struck_interaction_does_not_apply_low_velocity_pressure_swell",
        "three_note_pad_pressure_zero_must_recover_audio": "test_regression_three_note_pad_pressure_zero_recovers_actual_audio",
        "migrated_scale_paths_must_preserve_existing_order": "test_regression_migrated_scale_paths_preserve_order",
        "interval_grip_must_require_complete_timed_targets": "test_regression_interval_grip_requires_complete_timed_targets",
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
        self.page.locator('[data-testid="continue-without-midi"]').click()
        page_select_option = self.page.select_option

        def select_option_with_setup(*args, **kwargs):
            active_workspace = self.page.locator('.app-shell').get_attribute('data-workspace')
            if active_workspace != 'setup':
                self.page.locator('[data-testid="workspace-setup"]').click()
            try:
                return page_select_option(*args, **kwargs)
            finally:
                if active_workspace != 'setup':
                    self.page.locator(f'[data-testid="workspace-{active_workspace}"]').click()

        self.page.select_option = select_option_with_setup

    def tearDown(self):
        self.browser.close()
        self.pw.stop()

    def open_audio_drawer(self):
        if self.page.locator('.app-shell').get_attribute('data-workspace') != 'studio':
            self.page.locator('[data-testid="workspace-studio"]').click()
        practice_tools = self.page.locator('[data-testid="practice-tools"]')
        if practice_tools.count() and not practice_tools.evaluate("el => el.open"):
            practice_tools.locator("summary").click()
        drawer = self.page.locator('[data-testid="audio-drawer"]')
        if drawer.count() == 0:
            return
        if not drawer.evaluate("el => el.open"):
            drawer.locator("summary").click()

    def open_hardware_tools(self):
        if self.page.locator('.app-shell').get_attribute('data-workspace') != 'studio':
            self.page.locator('[data-testid="workspace-studio"]').click()
        hardware_tools = self.page.locator('[data-testid="hardware-tools"]')
        if hardware_tools.count() and not hardware_tools.evaluate("el => el.open"):
            hardware_tools.locator("summary").click()

    def test_every_stated_failure_has_named_regression_test(self):
        available = {name for name in dir(type(self)) if name.startswith("test_")}
        for failure_id, test_name in self.STATED_FAILURE_REGRESSIONS.items():
            self.assertIn(test_name, available, failure_id)

    def test_build_version_badge_is_visible_and_matches_runtime_cache_key(self):
        badge = self.page.locator('[data-testid="build-version"]')
        self.assertTrue(badge.is_visible())
        badge_box = badge.bounding_box()
        self.assertIsNotNone(badge_box)
        self.assertGreaterEqual(badge_box["width"], 45)
        self.assertLessEqual(badge_box["width"], 100)
        self.assertLessEqual(badge_box["height"], 24)
        self.assertIn("Build", badge.inner_text())
        version = badge.locator("b").inner_text()
        self.assertRegex(version, r"^Build \d+$")
        runtime = self.page.evaluate("() => window.SSLI_EXQUIS_BUILD")
        self.assertEqual(runtime["version"], version)
        self.assertRegex(runtime["timestamp"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [AP]M ET$")
        self.assertRegex(runtime["timestampUtc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertIn("ssli/index.html?exhibitHost=1&v=" + runtime["timestampUtc"], self.page.locator("#ssliEngineFrame").get_attribute("src"))

    def test_regression_build_metadata_does_not_dominate_practice_surface(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""() => {
          const badge = document.querySelector('[data-testid="build-version"]').getBoundingClientRect();
          const surface = document.querySelector('[data-testid="practice-surface"]').getBoundingClientRect();
          const style = getComputedStyle(document.querySelector('[data-testid="build-version"]'));
          return {
            badge: badge.toJSON(),
            surface: surface.toJSON(),
            position: style.position,
            widthShare: badge.width / surface.width
          };
        }""")
        self.assertNotEqual(metrics["position"], "fixed", metrics)
        self.assertLessEqual(metrics["widthShare"], 0.08, metrics)

    def test_regression_midi_is_the_hardware_first_launch_action(self):
        self.page.reload()
        gate = self.page.locator('[data-testid="connection-gate"]')
        primary = self.page.locator('[data-testid="enable-midi-gate"]')
        bypass = self.page.locator('[data-testid="continue-without-midi"]')
        self.assertTrue(gate.is_visible())
        self.assertTrue(primary.is_visible())
        self.assertTrue(bypass.is_visible())
        self.assertGreater(
            primary.bounding_box()["height"],
            bypass.bounding_box()["height"],
        )
        bypass.click()
        self.assertFalse(gate.is_visible())

    def test_regression_embedded_ssli_iframe_does_not_bind_web_midi_directly(self):
        frame = self.page.locator("#ssliEngineFrame")
        self.assertIn("exhibitHost=1", frame.get_attribute("src"))
        ssli_frame = next((candidate for candidate in self.page.frames if "ssli/index.html" in candidate.url), None)
        self.assertIsNotNone(ssli_frame)
        ssli_frame.wait_for_function("() => window.SynthLab && window.SynthLab.midi")
        midi_enabled = ssli_frame.evaluate("() => window.SynthLab.midi.isEnabled()")
        self.assertFalse(midi_enabled)

    def test_regression_ssli_voice_steal_cleanup_does_not_free_reused_voice(self):
        ssli_frame = next((candidate for candidate in self.page.frames if "ssli/index.html" in candidate.url), None)
        self.assertIsNotNone(ssli_frame)
        ssli_frame.wait_for_function("() => window.SynthLab && window.SynthLab.audio && window.SynthLab.audio.acquireVoice")
        result = ssli_frame.evaluate("""
        async () => {
          const audio = window.SynthLab.audio;
          const ctx = audio.getCtx();
          if (ctx && ctx.resume) {
            await ctx.resume();
          }
          const presets = window.SynthLab.presets;
          const pwmLead = presets && presets.getPresetsForEngineCategory
            ? (presets.getPresetsForEngineCategory('Subtractive', 'All') || []).find((preset) => preset && preset.name === 'PWM Lead')
            : null;
          if (pwmLead && presets.apply) {
            presets.apply(pwmLead, 0);
          }
          audio.initVoicePool();
          const voices = [];
          for (let midi = 0; midi < 80; midi += 1) {
            voices.push(audio.acquireVoice(0, midi));
          }
          const stolenAndReused = audio.acquireVoice(0, 81);
          const before = audio.getVoicePoolStats();
          await new Promise((resolve) => setTimeout(resolve, 80));
          const after = audio.getVoicePoolStats();
          [...new Set(voices.concat([stolenAndReused]))].forEach((voice) => {
            if (voice) audio.releaseVoice(voice, true);
          });
          return {
            before,
            after,
            reusedVoiceId: stolenAndReused && stolenAndReused.id
          };
        }
        """)
        self.assertEqual(result["before"]["currentlyActive"], 80, result)
        self.assertEqual(result["before"]["available"], 0, result)
        self.assertEqual(result["before"]["steals"], 1, result)
        self.assertEqual(result["after"]["currentlyActive"], 80, result)
        self.assertEqual(result["after"]["available"], 0, result)

    def test_regression_ssli_voice_pool_reclaims_available_emergency_voices_after_short_note_churn(self):
        ssli_frame = next((candidate for candidate in self.page.frames if "ssli/index.html" in candidate.url), None)
        self.assertIsNotNone(ssli_frame)
        ssli_frame.wait_for_function("() => window.SynthLab && window.SynthLab.audio && window.SynthLab.audio.acquireVoice")
        result = ssli_frame.evaluate("""
        async () => {
          const audio = window.SynthLab.audio;
          const ctx = audio.getCtx();
          if (ctx && ctx.resume) {
            await ctx.resume();
          }
          const presets = window.SynthLab.presets;
          const pwmLead = presets && presets.getPresetsForEngineCategory
            ? (presets.getPresetsForEngineCategory('Subtractive', 'All') || []).find((preset) => preset && preset.name === 'PWM Lead')
            : null;
          if (pwmLead && presets.apply) {
            presets.apply(pwmLead, 0);
          }
          audio.initVoicePool();
          let nullAtCycle = null;
          let maxTotalAllocated = 0;
          const snapshots = [];
          for (let cycle = 0; cycle < 90; cycle += 1) {
            const regularReuse = [];
            for (let midi = 0; midi < 80; midi += 1) {
              regularReuse.push(audio.acquireVoice(0, 4000 + cycle * 100 + midi));
            }
            regularReuse.forEach((voice) => {
              if (voice) audio.releaseVoice(voice, false);
            });
            const dropoutCandidate = audio.acquireVoice(0, 16000 + cycle);
            const stats = audio.getVoicePoolStats();
            maxTotalAllocated = Math.max(maxTotalAllocated, stats.totalAllocated);
            if (cycle % 10 === 0 || !dropoutCandidate) {
              snapshots.push({
                cycle,
                totalAllocated: stats.totalAllocated,
                available: stats.available,
                currentlyActive: stats.currentlyActive,
                steals: stats.steals,
                acquired: Boolean(dropoutCandidate)
              });
            }
            if (!dropoutCandidate) {
              nullAtCycle = cycle;
              break;
            }
            audio.releaseVoice(dropoutCandidate, false);
            await new Promise((resolve) => setTimeout(resolve, 125));
          }
          await new Promise((resolve) => setTimeout(resolve, 130));
          return {
            finalStats: audio.getVoicePoolStats(),
            maxTotalAllocated,
            nullAtCycle,
            snapshots
          };
        }
        """)
        self.assertIsNone(result["nullAtCycle"], result)
        self.assertLessEqual(result["maxTotalAllocated"], 82, result)

    def test_regression_hidden_ssli_iframe_reclaims_released_voices_without_animation_frames(self):
        ssli_frame = next((candidate for candidate in self.page.frames if "ssli/index.html" in candidate.url), None)
        self.assertIsNotNone(ssli_frame)
        ssli_frame.wait_for_function("() => window.SynthLab && window.SynthLab.audio && window.SynthLab.audio.acquireVoice")
        result = ssli_frame.evaluate("""
        async () => {
          const audio = window.SynthLab.audio;
          const originalRaf = window.requestAnimationFrame;
          window.requestAnimationFrame = () => 1;
          try {
            audio.initVoicePool();
            const voices = [];
            for (let midi = 0; midi < 80; midi += 1) {
              voices.push(audio.acquireVoice(0, midi));
            }
            voices.forEach((voice) => audio.releaseVoice(voice, false));
            const duringRelease = audio.getVoicePoolStats();
            await new Promise((resolve) => setTimeout(resolve, 250));
            const afterRelease = audio.getVoicePoolStats();
            return { duringRelease, afterRelease };
          } finally {
            window.requestAnimationFrame = originalRaf;
          }
        }
        """)
        self.assertEqual(result["duringRelease"]["available"], 0, result)
        self.assertEqual(result["afterRelease"]["available"], 80, result)
        self.assertEqual(result["afterRelease"]["freeStack"], 80, result)

    def test_regression_ssli_start_sustained_tracks_every_pwm_lead_short_note(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "subtractive")
        self.page.select_option('[data-testid="sound-category-select"]', "Leads")
        self.page.select_option('[data-testid="sound-preset-select"]', label="PWM Lead")
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
        self.open_hardware_tools()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        result = self.page.evaluate("""
        async () => {
          const input = window.__mockExquisInput;
          const log = document.querySelector('[data-testid="diagnostic-log"]');
          const events = [];
          const notes = [
            { midi: 52, channel: 8, velocity: 7 },
            { midi: 51, channel: 9, velocity: 4 },
            { midi: 53, channel: 10, velocity: 12 },
            { midi: 55, channel: 11, velocity: 1 },
            { midi: 57, channel: 12, velocity: 46 },
            { midi: 59, channel: 13, velocity: 11 },
            { midi: 60, channel: 14, velocity: 1 },
            { midi: 48, channel: 15, velocity: 11 },
            { midi: 50, channel: 2, velocity: 28 },
            { midi: 48, channel: 1, velocity: 27 },
            { midi: 48, channel: 4, velocity: 19 }
          ];
          for (let cycle = 0; cycle < 12; cycle += 1) {
            for (let i = 0; i < notes.length; i += 1) {
              const note = notes[i];
              input.onmidimessage({ data: [0x90 | note.channel, note.midi, note.velocity] });
              input.onmidimessage({ data: [0xD0 | note.channel, Math.max(1, note.velocity)] });
              await new Promise((resolve) => setTimeout(resolve, 8));
              input.onmidimessage({ data: [0xD0 | note.channel, 0] });
              input.onmidimessage({ data: [0x80 | note.channel, note.midi, 0] });
              await new Promise((resolve) => setTimeout(resolve, 125));
              const text = log.textContent;
              const lastAfterStart = text.match(/MIDI voices after-start [^\\n]+/g);
              events.push(lastAfterStart ? lastAfterStart[lastAfterStart.length - 1] : '');
            }
          }
          return {
            events,
            logText: log.textContent
          };
        }
        """)
        self.assertFalse(any("ssli=0" in event for event in result["events"]), result)
        self.assertNotIn("SSLI MIDI sustain failed", result["logText"])

    def test_regression_parent_rejects_ssli_sustain_start_without_tracked_voice(self):
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          const activeOscs = new Map();
          window.__ssliCalls = [];
          window.SynthLab = {
            presets: { apply() {} },
            audio: {
              getCtx() { return { state: 'running' }; },
              initEffectChain() {},
              getActiveOscillators() { return activeOscs; },
              getVoicePoolStats() { return { currentlyActive: 0, available: 160, freeStack: 0, totalAllocated: 160, steals: 80 }; },
              getCurrentInstrument() { return 0; },
              getInstrumentType() { return 'subtractive'; },
              getInstruments() { return [{ type: 'subtractive', settings: { volume: 100, filter: {}, effects: {} } }]; },
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
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90 | 4, 60, 11] })")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('SSLI MIDI sustain failed C4 missing active oscillator after start')")
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("poolActive=0 poolAvail=160 poolStack=0 poolTotal=160 steals=80", log)
        self.assertIn("MIDI voice start C4", log)
        self.assertNotIn("SSLI MIDI sustain start C4", log)

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
        self.assertIn("Audio:", self.page.locator('[data-testid="audio-status"]').inner_text())

    def test_regression_exercise_event_schema(self):
        events = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents")
        self.assertGreater(len(events), 0, events)
        first = events[0]
        self.assertEqual(first["type"], "note", first)
        self.assertEqual(first["targets"][0]["cellId"], first["cellId"], first)
        self.assertEqual(first["targets"][0]["midi"], first["midi"], first)
        self.assertIsInstance(first["targets"][0]["pc"], int, first)
        self.assertIn("fingering", first)
        self.assertIn("timing", first)
        self.assertTrue(first["valid"], first)
        self.assertTrue(all(event["valid"] for event in events), events)
        self.page.locator('[data-testid="test-audio"]').click()
        self.page.locator('[data-testid="test-audio"]').click()
        self.page.locator('[data-testid="play-scale"]').click()
        self.assertIn("Audio:", self.page.locator('[data-testid="audio-status"]').inner_text())

    def test_regression_simultaneous_grip_event_schema(self):
        grip = self.page.evaluate("""() => window.__exquisDebugBuildGripExerciseEvent({
          id: 'C-major-triad',
          targets: [
            { cellId: 'r5c3', midi: 48, pc: 0 },
            { cellId: 'r4c5', midi: 52, pc: 4 },
            { cellId: 'r3c7', midi: 55, pc: 7 }
          ],
          fingerAssignments: [
            { cellId: 'r5c3', finger: 5 },
            { cellId: 'r4c5', finger: 3 },
            { cellId: 'r3c7', finger: 1 }
          ]
        })""")
        self.assertEqual(grip["type"], "grip", grip)
        self.assertEqual(grip["timing"]["mode"], "simultaneous", grip)
        self.assertEqual(len(grip["targets"]), 3, grip)
        self.assertEqual(len(grip["fingering"]["assignments"]), 3, grip)
        self.assertTrue(grip["valid"], grip)

        duplicate_assignment = self.page.evaluate("""() => window.__exquisDebugBuildGripExerciseEvent({
          id: 'bad-grip',
          targets: [
            { cellId: 'r5c3', midi: 48, pc: 0 },
            { cellId: 'r4c5', midi: 52, pc: 4 },
            { cellId: 'r3c7', midi: 55, pc: 7 }
          ],
          fingerAssignments: [
            { cellId: 'r5c3', finger: 5 },
            { cellId: 'r5c3', finger: 3 },
            { cellId: 'r3c7', finger: 1 }
          ]
        })""")
        self.assertFalse(duplicate_assignment["valid"], duplicate_assignment)

    def test_regression_exercise_lifecycle_event_schema(self):
        events = self.page.evaluate("""() => window.__exquisDebugBuildExerciseLifecycleEvents()""")
        self.assertEqual([event["type"] for event in events], ["note", "hold", "release", "shift"], events)
        self.assertTrue(all(event["valid"] for event in events), events)
        self.assertEqual(events[3]["targets"], [], events[3])
        self.assertEqual(events[3]["movement"]["type"], "position-shift", events[3])

    def test_regression_interval_grip_requires_complete_timed_targets(self):
        result = self.page.evaluate("""() => window.__exquisDebugEvaluateGrip({
          id: 'C-E',
          type: 'grip',
          targets: [{ cellId: 'r5c3', midi: 48 }, { cellId: 'r4c5', midi: 52 }],
          fingering: { primary: 5, assignments: [{ cellId: 'r5c3', finger: 5 }, { cellId: 'r4c5', finger: 3 }] },
          timing: { mode: 'simultaneous', toleranceMs: 80 }
        }, [
          { midi: 48, cellId: 'r5c3', at: 1000 },
          { midi: 52, cellId: 'r4c5', at: 1060 }
        ])""")
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["outcome"], "complete", result)

        partial = self.page.evaluate("""() => window.__exquisDebugEvaluateGrip({
          id: 'C-E', type: 'grip', targets: [{ cellId: 'r5c3', midi: 48 }, { cellId: 'r4c5', midi: 52 }],
          fingering: { primary: 5, assignments: [] }, timing: { mode: 'simultaneous', toleranceMs: 80 }
        }, [{ midi: 48, cellId: 'r5c3', at: 1000 }])""")
        self.assertFalse(partial["accepted"], partial)
        self.assertEqual(partial["outcome"], "partial", partial)

        late = self.page.evaluate("""() => window.__exquisDebugEvaluateGrip({
          id: 'C-E', type: 'grip', targets: [{ cellId: 'r5c3', midi: 48 }, { cellId: 'r4c5', midi: 52 }],
          fingering: { primary: 5, assignments: [] }, timing: { mode: 'simultaneous', toleranceMs: 80 }
        }, [{ midi: 48, cellId: 'r5c3', at: 1000 }, { midi: 52, cellId: 'r4c5', at: 1090 }])""")
        self.assertFalse(late["accepted"], late)
        self.assertEqual(late["outcome"], "late", late)

    def test_regression_grip_accepts_pitch_only_hardware_evidence_for_duplicate_target(self):
        result = self.page.evaluate("""() => window.__exquisDebugEvaluateGrip({
          id: 'F-major-resolution',
          type: 'grip',
          targets: [
            { cellId: 'r3c1', midi: 53 },
            { cellId: 'r2c2', midi: 57 },
            { cellId: 'r1c1', midi: 60 }
          ],
          fingering: { primary: 5, assignments: [] },
          timing: { mode: 'simultaneous', toleranceMs: 80 }
        }, [
          { midi: 53, cellId: 'r3c1', at: 1000 },
          { midi: 57, cellId: 'r2c2', at: 1020 },
          { midi: 60, cellId: '', cellIds: ['r1c1', 'r2c5'], at: 1040 }
        ])""")
        self.assertTrue(result["accepted"], result)
        self.assertEqual(result["outcome"], "complete", result)

    def test_major_triad_exercise_emits_selected_root_grip(self):
        self.page.select_option('[data-testid="exercise-select"]', "major_triad")
        snapshot = self.page.evaluate("() => window.__exquisDebugSnapshot()")
        self.assertEqual(len(snapshot["exerciseEvents"]), 1, snapshot)
        event = snapshot["exerciseEvents"][0]
        self.assertEqual(event["type"], "grip", event)
        self.assertEqual([target["midi"] for target in event["targets"]], [48, 52, 55], event)
        self.assertTrue(event["valid"], event)
        self.assertEqual(self.page.locator('[data-testid="step-readout"]').inner_text(), "1 / 1")
        self.assertEqual(self.page.locator('[data-testid="current-note"]').inner_text(), "C3 + E3 + G3")

    def test_regression_harmony_fixture_resolves_minor_first_inversion_to_exact_cells(self):
        fixture = self.page.evaluate("""() => window.__exquisDebugBuildHarmonyGripFixture({
          id: 'minor-first-inversion',
          quality: 'minor',
          inversion: 1,
          rootMidi: 48
        })""")
        self.assertTrue(fixture["valid"], fixture)
        self.assertEqual(fixture["musicalIntent"], {"type": "triad", "quality": "minor", "inversion": "first"}, fixture)
        self.assertEqual([target["midi"] for target in fixture["targets"]], [51, 55, 60], fixture)
        self.assertEqual(len({target["cellId"] for target in fixture["targets"]}), 3, fixture)

    def test_regression_harmony_fixtures_preserve_quality_through_inversions(self):
        fixtures = self.page.evaluate("""() => [
          ['major', 0, [48, 52, 55]], ['major', 1, [52, 55, 60]], ['major', 2, [55, 60, 64]],
          ['minor', 0, [48, 51, 55]], ['minor', 1, [51, 55, 60]], ['minor', 2, [55, 60, 63]],
          ['diminished', 0, [48, 51, 54]], ['diminished', 1, [51, 54, 60]], ['diminished', 2, [54, 60, 63]],
          ['augmented', 0, [48, 52, 56]], ['augmented', 1, [52, 56, 60]], ['augmented', 2, [56, 60, 64]]
        ].map(([quality, inversion, expected]) => {
          const event = window.__exquisDebugBuildHarmonyGripFixture({ quality, inversion, rootMidi: 48 });
          return { quality, inversion, expected, event };
        })""")
        for fixture in fixtures:
            event = fixture["event"]
            self.assertTrue(event and event["valid"], fixture)
            self.assertEqual([target["midi"] for target in event["targets"]], fixture["expected"], fixture)

    def test_regression_harmony_triad_lesson_exposes_quality_and_inversion(self):
        self.page.select_option('[data-testid="exercise-select"]', "harmony_triad")
        self.page.select_option('[data-testid="harmony-quality-select"]', "minor")
        self.page.select_option('[data-testid="harmony-inversion-select"]', "2")
        event = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents[0]")
        self.assertTrue(self.page.locator('[data-testid="harmony-triad-controls"]').is_visible())
        self.assertEqual(event["musicalIntent"], {"type": "triad", "quality": "minor", "inversion": "second"}, event)
        self.assertEqual([target["midi"] for target in event["targets"]], [55, 60, 63], event)
        self.assertEqual(self.page.locator('[data-testid="coach-now-playing"]').inner_text(), "G3 + C4 + D#4")

    def test_regression_harmony_triad_scores_an_inverted_minor_grip_once(self):
        self.page.select_option('[data-testid="exercise-select"]', "harmony_triad")
        self.page.select_option('[data-testid="harmony-quality-select"]', "minor")
        self.page.select_option('[data-testid="harmony-inversion-select"]', "2")
        self.page.evaluate("""() => {
          window.__harmonyInput = { id: 'harmony-input', name: 'Harmony Input', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({ inputs: { forEach: (cb) => cb(window.__harmonyInput) }, outputs: { forEach: () => {} }, onstatechange: null });
        }""")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__harmonyInput && window.__harmonyInput.onmidimessage")
        for midi, channel in [(55, 0), (60, 1), (63, 2)]:
            self.page.evaluate("(args) => window.__harmonyInput.onmidimessage({ data: [0x90 | args.channel, args.midi, 84] })", {"midi": midi, "channel": channel})
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-feedback\"]').textContent.includes('Correct grip')")
        self.assertIn("Score: 1 correct / 0 missed", self.page.locator('[data-testid="coach-progress"]').inner_text())
        self.assertEqual(self.page.locator('[data-testid="step-readout"]').inner_text(), "1 / 1")

    def test_regression_voice_leading_chooses_common_tone_minimum_motion_destination(self):
        transition = self.page.evaluate("""() => window.__exquisDebugBuildVoiceLeadingTransition({
          from: { quality: 'major', rootMidi: 48, inversion: 0 },
          to: { quality: 'major', rootMidi: 41 }
        })""")
        self.assertIsNotNone(transition)
        self.assertEqual([target["midi"] for target in transition["from"]["targets"]], [48, 52, 55], transition)
        self.assertEqual(transition["to"]["musicalIntent"]["inversion"], "second", transition)
        self.assertEqual([target["midi"] for target in transition["to"]["targets"]], [48, 53, 57], transition)
        self.assertEqual(transition["anchorMidis"], [48], transition)
        self.assertEqual(transition["movementSemitones"], 3, transition)

    def test_regression_voice_leading_lesson_presents_source_then_common_tone_destination(self):
        self.page.select_option('[data-testid="exercise-select"]', "voice_leading")
        events = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents")
        self.assertTrue(self.page.locator('[data-testid="harmony-triad-controls"]').is_visible())
        self.assertEqual(len(events), 2, events)
        self.assertEqual([target["midi"] for target in events[0]["targets"]], [48, 52, 55], events)
        self.assertEqual([target["midi"] for target in events[1]["targets"]], [48, 53, 57], events)
        self.assertEqual(events[1]["musicalIntent"]["anchorMidis"], [48], events)

    def test_regression_voice_leading_scores_source_and_destination_grips_in_sequence(self):
        self.page.select_option('[data-testid="exercise-select"]', "voice_leading")
        self.page.evaluate("""() => {
          window.__voiceLeadingInput = { id: 'voice-leading-input', name: 'Voice Leading Input', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({ inputs: { forEach: (cb) => cb(window.__voiceLeadingInput) }, outputs: { forEach: () => {} }, onstatechange: null });
        }""")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__voiceLeadingInput && window.__voiceLeadingInput.onmidimessage")

        def send_notes(notes, status):
            for midi, channel in zip(notes, range(len(notes))):
                self.page.evaluate("(args) => window.__voiceLeadingInput.onmidimessage({ data: [args.status | args.channel, args.midi, 84] })", {"midi": midi, "channel": channel, "status": status})

        send_notes([48, 52, 55], 0x90)
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-progress\"]').textContent.includes('1 correct / 0 missed')")
        send_notes([48, 52, 55], 0x80)
        send_notes([48, 53, 57], 0x90)
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-progress\"]').textContent.includes('2 correct / 0 missed')")
        self.assertIn("Step 1 / 2", self.page.locator('[data-testid="coach-progress"]').inner_text())

    def test_regression_ear_to_gesture_conceals_targets_and_prompt_playback_preserves_score(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'ear')
        self.page.select_option('[data-testid="exercise-select"]', "ear_major_third")
        event = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents[0]")
        self.assertEqual(event["musicalIntent"], {"type": "heard-interval", "quality": "major-third", "promptMidis": [48, 52], "concealTargets": True}, event)
        self.assertEqual(self.page.locator('[data-testid="coach-now-playing"]').inner_text(), "Listen, then answer")
        self.assertEqual(self.page.locator('[data-testid="exquis-key"].in-path').count(), 0)
        self.assertFalse(self.page.locator('[data-testid="repertoire-section-panel"]').is_visible())
        score_before = self.page.locator('[data-testid="coach-progress"]').inner_text()
        self.page.locator('[data-testid="coach-next-action"]').click()
        self.assertEqual(self.page.locator('[data-testid="coach-progress"]').inner_text(), score_before)
        self.assertIn("Listen for the interval", self.page.locator('[data-testid="coach-feedback"]').inner_text())

    def test_regression_ear_to_gesture_scores_exact_interval_and_repairs_wrong_interval(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'ear')
        self.page.select_option('[data-testid="exercise-select"]', "ear_major_third")
        self.page.evaluate("""() => {
          window.__earInput = { id: 'ear-input', name: 'Ear Input', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({ inputs: { forEach: (cb) => cb(window.__earInput) }, outputs: { forEach: () => {} }, onstatechange: null });
        }""")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__earInput && window.__earInput.onmidimessage")

        def send(notes):
            for midi, channel in zip(notes, range(len(notes))):
                self.page.evaluate("(args) => window.__earInput.onmidimessage({ data: [0x90 | args.channel, args.midi, 84] })", {"midi": midi, "channel": channel})

        send([48, 51])
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-progress\"]').textContent.includes('0 correct / 1 missed')")
        self.assertEqual(self.page.locator('[data-testid="coach-now-playing"]').inner_text(), "Listen, then answer")
        send([48, 52])
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-progress\"]').textContent.includes('1 correct / 1 missed')")
        self.assertIn("Correct grip", self.page.locator('[data-testid="coach-feedback"]').inner_text())

    def test_regression_ear_to_gesture_interval_fixtures_keep_minor_and_major_prompts_exact(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'ear')
        fixtures = self.page.evaluate("""() => ['ear_minor_third', 'ear_major_third', 'ear_perfect_fourth', 'ear_perfect_fifth'].map((exerciseId) => {
          document.querySelector('[data-testid="exercise-select"]').value = exerciseId;
          document.querySelector('[data-testid="exercise-select"]').dispatchEvent(new Event('change', { bubbles: true }));
          return { exerciseId, event: window.__exquisDebugSnapshot().exerciseEvents[0] };
        })""")
        self.assertEqual(fixtures[0]["event"]["musicalIntent"]["promptMidis"], [48, 51], fixtures)
        self.assertEqual(fixtures[0]["event"]["musicalIntent"]["quality"], "minor-third", fixtures)
        self.assertEqual(fixtures[1]["event"]["musicalIntent"]["promptMidis"], [48, 52], fixtures)
        self.assertEqual(fixtures[1]["event"]["musicalIntent"]["quality"], "major-third", fixtures)
        self.assertEqual(fixtures[2]["event"]["musicalIntent"]["promptMidis"], [48, 53], fixtures)
        self.assertEqual(fixtures[2]["event"]["musicalIntent"]["quality"], "perfect-fourth", fixtures)
        self.assertEqual(fixtures[3]["event"]["musicalIntent"]["promptMidis"], [48, 55], fixtures)
        self.assertEqual(fixtures[3]["event"]["musicalIntent"]["quality"], "perfect-fifth", fixtures)

    def test_regression_ear_to_gesture_perfect_fifth_scores_exact_grip(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'ear')
        self.page.select_option('[data-testid="exercise-select"]', "ear_perfect_fifth")
        self.page.evaluate("""() => {
          window.__fifthInput = { id: 'fifth-input', name: 'Fifth Input', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({ inputs: { forEach: (cb) => cb(window.__fifthInput) }, outputs: { forEach: () => {} }, onstatechange: null });
        }""")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__fifthInput && window.__fifthInput.onmidimessage")
        for midi, channel in [(48, 0), (55, 1)]:
            self.page.evaluate("(args) => window.__fifthInput.onmidimessage({ data: [0x90 | args.channel, args.midi, 84] })", {"midi": midi, "channel": channel})
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-progress\"]').textContent.includes('1 correct / 0 missed')")
        self.assertIn("Correct grip", self.page.locator('[data-testid="coach-feedback"]').inner_text())

    def test_regression_progression_fixture_resolves_c_major_i_iv_v_i_to_exact_triads(self):
        progression = self.page.evaluate("() => window.__exquisDebugBuildProgressionFixture('c-major-i-iv-v-i')")
        self.assertEqual(progression["title"], "C major I-IV-V-I", progression)
        self.assertEqual([[target["midi"] for target in event["targets"]] for event in progression["events"]], [[48, 52, 55], [41, 45, 48], [43, 47, 50], [48, 52, 55]], progression)
        self.assertTrue(all(event["valid"] for event in progression["events"]), progression)

    def test_regression_progression_lesson_presents_i_iv_v_i_in_order(self):
        self.page.select_option('[data-testid="exercise-select"]', "c_major_progression")
        events = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents")
        self.assertEqual([event["musicalIntent"]["degree"] for event in events], ["I", "IV", "V", "I"], events)
        self.assertEqual([target["midi"] for target in events[0]["targets"]], [48, 52, 55], events)
        self.assertEqual([target["midi"] for target in events[1]["targets"]], [41, 45, 48], events)
        self.assertIn("Progression I", self.page.locator('[data-testid="coach-action-cue"]').inner_text())

    def test_regression_progression_lesson_retains_wrong_chord_and_advances_on_correct_chord(self):
        self.page.select_option('[data-testid="exercise-select"]', "c_major_progression")
        self.page.evaluate("""() => {
          window.__progressionInput = { id: 'progression-input', name: 'Progression Input', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({ inputs: { forEach: (cb) => cb(window.__progressionInput) }, outputs: { forEach: () => {} }, onstatechange: null });
        }""")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__progressionInput && window.__progressionInput.onmidimessage")

        def play(notes):
            for midi, channel in zip(notes, range(len(notes))):
                self.page.evaluate("(args) => window.__progressionInput.onmidimessage({ data: [0x90 | args.channel, args.midi, 84] })", {"midi": midi, "channel": channel})

        play([48, 51, 55])
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-progress\"]').textContent.includes('0 correct / 1 missed')")
        self.assertEqual(self.page.locator('[data-testid="step-readout"]').inner_text(), "1 / 4")
        play([48, 52, 55])
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-progress\"]').textContent.includes('1 correct / 1 missed')")
        self.assertEqual(self.page.locator('[data-testid="step-readout"]').inner_text(), "2 / 4")

    def test_regression_progression_fixture_resolves_c_major_ii_v_i_to_exact_triads(self):
        progression = self.page.evaluate("() => window.__exquisDebugBuildProgressionFixture('c-major-ii-v-i')")
        self.assertEqual(progression["title"], "C major ii-V-I", progression)
        self.assertEqual([event["musicalIntent"]["degree"] for event in progression["events"]], ["ii", "V", "I"], progression)
        self.assertEqual([[target["midi"] for target in event["targets"]] for event in progression["events"]], [[50, 53, 57], [43, 47, 50], [48, 52, 55]], progression)

    def test_regression_ii_v_i_fixture_transposes_functions_and_voicings_for_c_f_and_bb(self):
        fixtures = self.page.evaluate("""() => [
          { tonicPc: 0, targets: [[50, 53, 57], [43, 47, 50], [48, 52, 55]] },
          { tonicPc: 5, targets: [[55, 58, 62], [48, 52, 55], [53, 57, 60]] },
          { tonicPc: 10, targets: [[60, 63, 67], [53, 57, 60], [58, 62, 65]] }
        ].map((expected) => {
          const progression = window.__exquisDebugBuildProgressionFixture('c-major-ii-v-i', expected.tonicPc);
          return {
            tonicPc: expected.tonicPc,
            title: progression && progression.title,
            degrees: progression && progression.events.map((event) => event.musicalIntent.degree),
            qualities: progression && progression.events.map((event) => event.musicalIntent.quality),
            targets: progression && progression.events.map((event) => event.targets.map((target) => target.midi))
          };
        })""")
        self.assertEqual([fixture["degrees"] for fixture in fixtures], [["ii", "V", "I"]] * 3, fixtures)
        self.assertEqual([fixture["qualities"] for fixture in fixtures], [["minor", "major", "major"]] * 3, fixtures)
        self.assertEqual([fixture["targets"] for fixture in fixtures], [
            [[50, 53, 57], [43, 47, 50], [48, 52, 55]],
            [[55, 58, 62], [48, 52, 55], [53, 57, 60]],
            [[60, 63, 67], [53, 57, 60], [58, 62, 65]]
        ], fixtures)

    def test_regression_ii_v_i_lesson_rebuilds_from_the_selected_tonic(self):
        self.page.select_option('[data-testid="exercise-select"]', "c_major_ii_v_i")
        observed = []
        for tonic_pc in ["0", "5", "10"]:
            self.page.select_option('[data-testid="tonic-select"]', tonic_pc)
            observed.append(self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents.map((event) => event.targets.map((target) => target.midi))"))
        self.assertEqual(observed, [
            [[50, 53, 57], [43, 47, 50], [48, 52, 55]],
            [[55, 58, 62], [48, 52, 55], [53, 57, 60]],
            [[60, 63, 67], [53, 57, 60], [58, 62, 65]]
        ])

    def test_regression_f_major_resolution_uses_the_compact_centerward_voicing(self):
        progression = self.page.evaluate("() => window.__exquisDebugBuildProgressionFixture('c-major-ii-v-i', 5)")
        resolution = progression["events"][2]
        self.assertEqual([target["midi"] for target in resolution["targets"]], [53, 57, 60], resolution)
        self.assertEqual([target["cellId"] for target in resolution["targets"]], ["r3c1", "r2c2", "r1c1"], resolution)

    def test_regression_progression_library_templates_resolve_playable_chords_across_major_keys(self):
        observed = self.page.evaluate("""() => {
          const ids = ['c-major-i-v-vi-iv', 'c-major-i-vi-ii-v', 'c-major-12-bar-blues'];
          return [0, 5, 10].map((tonicPc) => ids.map((id) => {
            const progression = window.__exquisDebugBuildProgressionFixture(id, tonicPc);
            return {
              id,
              title: progression && progression.title,
              degrees: progression && progression.events.map((event) => event.musicalIntent.degree),
              valid: progression && progression.events.every((event) => event.valid),
              eventCount: progression && progression.events.length
            };
          }));
        }""")
        expected_degrees = {
            "c-major-i-v-vi-iv": ["I", "V", "vi", "IV"],
            "c-major-i-vi-ii-v": ["I", "vi", "ii", "V"],
            "c-major-12-bar-blues": ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"]
        }
        expected_titles = ["C", "F", "Bb"]
        for tonic_name, fixtures in zip(expected_titles, observed):
            self.assertEqual([fixture["id"] for fixture in fixtures], list(expected_degrees), fixtures)
            self.assertTrue(all(fixture["valid"] for fixture in fixtures), fixtures)
            self.assertTrue(all(fixture["title"].startswith(tonic_name + " major") for fixture in fixtures), fixtures)
            for fixture in fixtures:
                self.assertEqual(fixture["degrees"], expected_degrees[fixture["id"]], fixture)

    def test_regression_dorian_vamp_transposes_and_resolves_as_playable_minor_to_major_pair(self):
        observed = self.page.evaluate("""() => [0, 5, 10].map((tonicPc) => {
          const progression = window.__exquisDebugBuildProgressionFixture('c-dorian-i-iv-vamp', tonicPc);
          return {
            title: progression && progression.title,
            degrees: progression && progression.events.map((event) => event.musicalIntent.degree),
            qualities: progression && progression.events.map((event) => event.musicalIntent.quality),
            targetMidis: progression && progression.events.map((event) => event.targets.map((target) => target.midi)),
            valid: progression && progression.events.every((event) => event.valid)
          };
        })""")
        self.assertEqual([item["title"] for item in observed], ["C Dorian i-IV vamp", "F Dorian i-IV vamp", "Bb Dorian i-IV vamp"], observed)
        self.assertTrue(all(item["valid"] for item in observed), observed)
        self.assertTrue(all(item["degrees"] == ["i", "IV", "i", "IV"] for item in observed), observed)
        self.assertTrue(all(item["qualities"] == ["minor", "major", "minor", "major"] for item in observed), observed)
        self.assertEqual([item["targetMidis"][:2] for item in observed], [
            [[36, 39, 43], [41, 45, 48]],
            [[41, 44, 48], [46, 50, 53]],
            [[46, 49, 53], [51, 55, 58]]
        ], observed)

    def test_regression_exercise_order_remains_stable_when_scale_changes(self):
        self.page.select_option('[data-testid="scale-select"]', 'dorian')
        dorian_options = self.page.locator('[data-testid="exercise-select"] option').evaluate_all("elements => elements.map((element) => ({ value: element.value, label: element.textContent }))")
        self.assertEqual(dorian_options, [
            {"value": "root_octave", "label": "Root to octave"},
            {"value": "two_octaves", "label": "Two octaves"},
            {"value": "inner_ladder", "label": "Inner-chain ladder"},
            {"value": "root_returns", "label": "Root returns"}
        ], dorian_options)
        self.page.select_option('[data-testid="scale-select"]', 'ionian')
        ionian_options = self.page.locator('[data-testid="exercise-select"] option').evaluate_all("elements => elements.map((element) => ({ value: element.value, label: element.textContent }))")
        self.assertEqual(ionian_options, dorian_options)

    def test_regression_exercise_chooser_uses_explicit_families_without_scale_driven_reordering(self):
        families = self.page.locator('[data-testid="exercise-family-select"] option').evaluate_all("elements => elements.map((element) => ({ value: element.value, label: element.textContent }))")
        self.assertEqual(families, [
            {"value": "technique", "label": "Technique"},
            {"value": "shapes", "label": "Shapes"},
            {"value": "progressions", "label": "Progressions"},
            {"value": "ear", "label": "Ear training"}
        ], families)
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.assertEqual(self.page.locator('[data-testid="progression-genre-select"]').input_value(), 'starter')
        self.assertEqual(self.page.locator('[data-testid="exercise-select"]').input_value(), 'major_i_iv_vi_v')
        self.assertEqual(self.page.locator('[data-testid="scale-select"]').input_value(), 'ionian')
        progression_options = self.page.locator('[data-testid="exercise-select"] option').evaluate_all("elements => elements.map((element) => element.value)")
        self.assertEqual(progression_options, [
            'dorian_i_iv_vamp', 'major_i_iv_vi_v', 'major_i_iii_iv_v', 'major_i_ii_vi_iv',
            'major_circle_of_fifths', 'minor_i_iv_v_i', 'minor_i_bVII_bVI_bVII', 'dorian_i_bVII_iv',
            'phrygian_i_bII_vamp', 'c_major_progression', 'c_major_ii_v_i', 'major_i_v_vi_iv',
            'major_i_vi_ii_v', 'major_12_bar_blues'
        ], progression_options)
        self.page.select_option('[data-testid="scale-select"]', 'dorian')
        self.assertEqual(self.page.locator('[data-testid="exercise-family-select"]').input_value(), 'progressions')
        self.assertEqual(self.page.locator('[data-testid="exercise-select"] option').evaluate_all("elements => elements.map((element) => element.value)"), progression_options)
        self.page.select_option('[data-testid="exercise-select"]', 'dorian_i_iv_vamp')
        self.assertEqual(self.page.locator('[data-testid="exercise-family-select"]').input_value(), 'progressions')

    def test_regression_progressions_open_with_a_major_starter_lesson(self):
        self.page.select_option('[data-testid="scale-select"]', 'dorian')
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.assertEqual(self.page.locator('[data-testid="exercise-select"]').input_value(), 'major_i_iv_vi_v')
        self.assertEqual(self.page.locator('[data-testid="scale-select"]').input_value(), 'ionian')

    def test_studio_reconnect_exquis_button_uses_the_same_connection_flow(self):
        self.page.evaluate("""() => {
          window.__landingMidiInput = { id: 'landing-midi', name: 'Landing MIDI', manufacturer: 'Exquis', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (callback) => callback(window.__landingMidiInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }""")
        self.page.locator('[data-testid="workspace-studio"]').click()
        self.assertEqual(self.page.locator('[data-testid="enable-midi"]').inner_text(), 'Reconnect Exquis')
        self.open_hardware_tools()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__landingMidiInput.onmidimessage !== null")
        self.assertIn('Landing MIDI', self.page.locator('[data-testid="midi-status"]').inner_text())

    def test_regression_progression_library_offers_a_broad_transposable_curriculum(self):
        fixture_ids = [
            'c-dorian-i-iv-vamp', 'c-major-i-iv-vi-v', 'c-major-i-iii-iv-v', 'c-major-i-ii-vi-iv',
            'c-major-circle-of-fifths', 'c-minor-i-iv-v-i', 'c-minor-i-bVII-bVI-bVII',
            'c-dorian-i-bVII-iv', 'c-phrygian-i-bII-vamp', 'c-major-i-iv-v-i', 'c-major-ii-v-i',
            'c-major-i-v-vi-iv', 'c-major-i-vi-ii-v', 'c-major-12-bar-blues'
        ]
        observed = self.page.evaluate("""(fixtureIds) => [0, 5, 10].map((tonicPc) => fixtureIds.map((id) => {
          const progression = window.__exquisDebugBuildProgressionFixture(id, tonicPc);
          return { id, valid: !!progression && progression.events.every((event) => event.valid), count: progression && progression.events.length };
        }))""", fixture_ids)
        self.assertEqual(len(fixture_ids), 14)
        self.assertTrue(all(item["valid"] and item["count"] >= 3 for key in observed for item in key), observed)

    def test_regression_ssli_genre_progression_library_remains_browsable_and_playable(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.assertTrue(self.page.locator('[data-testid="progression-genre-control"]').is_visible())
        genres = self.page.locator('[data-testid="progression-genre-select"] option').evaluate_all("elements => elements.map((element) => ({ value: element.value, label: element.textContent }))")
        self.assertEqual(genres[0], {"value": "starter", "label": "Starter repertoire"}, genres)
        self.assertEqual([genre["label"] for genre in genres[1:]], [
            'Pop & Rock', 'Jazz', 'Blues', 'Classical', 'R&B / Soul', 'EDM / Electronic', 'Folk / Country',
            'Film / Cinematic', 'Theory: Building Blocks', 'Theory: Mediant Subs', 'Reggaeton / Latin Pop',
            'Gospel / Worship', 'Bossa Nova / MPB', 'Prog Rock / Art Rock', 'Ambient / Drone'
        ], genres)
        self.page.select_option('[data-testid="progression-genre-select"]', 'ssli-1')
        jazz_options = self.page.locator('[data-testid="exercise-select"] option').evaluate_all("elements => elements.map((element) => ({ value: element.value, label: element.textContent }))")
        self.assertEqual(len(jazz_options), 31, jazz_options)
        self.assertEqual(jazz_options[0], {"value": "ssli_progression_1_0", "label": "ii-V-I - Jazz cadence foundation"}, jazz_options)
        self.page.select_option('[data-testid="exercise-select"]', 'ssli_progression_1_0')
        events = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents")
        self.assertEqual([event["musicalIntent"]["degree"] for event in events], ['ii', 'V', 'I'], events)
        result = self.page.evaluate("""() => {
          const groups = window.SSLI_VENDOR.progressionGroups;
          const invalid = [];
          for (const tonicPc of [0, 5, 10]) {
            groups.forEach((group, genreIndex) => group.progressions.forEach((_progression, progressionIndex) => {
              const fixture = window.__exquisDebugBuildSsliProgressionFixture(genreIndex, progressionIndex, tonicPc, 'ionian');
              if (!fixture || !fixture.events.every((event) => event.valid)) invalid.push({ tonicPc, genreIndex, progressionIndex });
            }));
          }
          return { genres: groups.length, progressions: groups.reduce((total, group) => total + group.progressions.length, 0), invalid };
        }""")
        self.assertEqual(result["genres"], 15, result)
        self.assertEqual(result["progressions"], 466, result)
        self.assertEqual(result["invalid"], [], result)

    def test_regression_major_progression_replaces_minor_scale_path_with_current_chord_targets(self):
        self.page.select_option('[data-testid="scale-select"]', 'aeolian')
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.page.select_option('[data-testid="progression-genre-select"]', 'starter')
        self.page.select_option('[data-testid="exercise-select"]', 'major_i_iv_vi_v')
        self.assertEqual(self.page.locator('[data-testid="scale-select"]').input_value(), 'ionian')
        visible = self.page.locator('[data-testid="exquis-key"]').evaluate_all("""keys => keys
          .filter(key => key.classList.contains('hardware-lit') || key.classList.contains('in-path') || key.classList.contains('in-scale'))
          .map(key => key.dataset.cellId)""")
        hardware_lit = self.page.locator('.key.hardware-lit').evaluate_all("keys => keys.map(key => key.dataset.cellId)")
        chord_targets = self.page.locator('.key.current-grip-target').evaluate_all("keys => keys.map(key => key.dataset.cellId)")
        self.assertEqual(sorted(visible), sorted(hardware_lit))
        self.assertGreater(len(hardware_lit), 0)
        self.assertEqual(len(chord_targets), 3)

    def test_regression_imported_progression_catalog_uses_learner_facing_labels(self):
        source_metadata = self.page.evaluate("""() => window.SSLI_VENDOR.progressionGroups.flatMap((group) => (
          group.progressions.map((progression) => ({ name: progression.name, usage: progression.usage }))
        ))""")
        self.assertEqual(len(source_metadata), 466, source_metadata)
        self.assertTrue(all(item["name"] and item["usage"] for item in source_metadata), source_metadata)
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.page.select_option('[data-testid="progression-genre-select"]', 'ssli-0')
        labels = self.page.locator('[data-testid="exercise-select"] option').all_text_contents()
        self.assertTrue(all(' - ' in label for label in labels), labels)
        self.assertEqual(labels[0], 'I-V-vi-IV - Most popular modern pop', labels)
        self.assertEqual(self.page.locator('[data-testid="exercise-control"] legend').inner_text(), 'Progression')

    def test_regression_progressions_offer_global_and_per_chord_voicing_controls(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.page.select_option('[data-testid="progression-genre-select"]', 'ssli-0')
        self.page.select_option('[data-testid="exercise-select"]', 'ssli_progression_0_0')
        self.assertTrue(self.page.locator('[data-testid="progression-voicing-panel"]').is_visible())
        self.assertEqual(self.page.locator('[data-testid="progression-voicing-title"]').inner_text(), 'Chord progression')
        self.assertEqual(self.page.locator('[data-testid="progression-global-note-count"]').input_value(), '3')
        rows = self.page.locator('[data-testid="progression-chord-row"]')
        self.assertEqual(rows.count(), 4)
        self.page.select_option('[data-testid="progression-global-note-count"]', '4')
        self.page.select_option('[data-testid="progression-global-inversion"]', '1')
        first_targets = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents[0].targets")
        self.assertEqual(len(first_targets), 4, first_targets)
        self.assertTrue(all(3 <= int(target["cellId"].split("c")[0][1:]) <= 7 for target in first_targets), first_targets)
        first_row = rows.nth(0)
        self.assertEqual(first_row.locator('[data-testid="progression-chord-degree"]').inner_text(), 'I')
        first_row.locator('[data-testid="progression-chord-note-count"]').select_option('2')
        self.assertEqual(first_row.locator('[data-testid="progression-chord-note-count"]').input_value(), '2')
        per_chord_targets = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents[0].targets.map((target) => target.midi)")
        self.assertEqual(len(per_chord_targets), 2, per_chord_targets)
        first_row = self.page.locator('[data-testid="progression-chord-row"]').nth(0)
        first_row.locator('[data-testid="progression-chord-inversion"]').select_option('0')
        inverted_targets = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents[0].targets.map((target) => target.midi)")
        self.assertNotEqual(inverted_targets, per_chord_targets, {"before": per_chord_targets, "after": inverted_targets})
        for note_count in ['2', '3', '4', '5']:
            self.page.select_option('[data-testid="progression-global-note-count"]', note_count)
            self.page.select_option('[data-testid="progression-global-inversion"]', str(int(note_count) - 1))
            target_lengths = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents.map((event) => event.targets.length)")
            self.assertEqual(target_lengths, [int(note_count)] * 4, {"noteCount": note_count, "lengths": target_lengths})

    def test_regression_chord_fingering_uses_distinct_labels_from_sequence_fingering(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.page.select_option('[data-testid="progression-genre-select"]', 'ssli-0')
        self.page.select_option('[data-testid="exercise-select"]', 'ssli_progression_0_0')
        self.page.select_option('[data-testid="progression-global-note-count"]', '5')
        chord_fingers = self.page.locator('.key.current-grip-target .finger')
        self.assertEqual(chord_fingers.count(), 5)
        self.assertEqual(sorted(chord_fingers.all_text_contents()), ['1', '2', '3', '4', '5'])
        self.assertTrue(all(
            label.startswith('Chord finger ')
            for label in chord_fingers.evaluate_all("els => els.map(el => el.getAttribute('aria-label'))")
        ))
        self.page.select_option('[data-testid="exercise-family-select"]', 'technique')
        sequence_fingers = self.page.locator('.key.current .finger')
        self.assertGreater(sequence_fingers.count(), 0)
        self.assertTrue(all(
            label.startswith('Sequence finger ')
            for label in sequence_fingers.evaluate_all("els => els.map(el => el.getAttribute('aria-label'))")
        ))

    def test_regression_exquis_chord_fingers_follow_adjacent_button_order(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.page.select_option('[data-testid="progression-genre-select"]', 'ssli-0')
        self.page.select_option('[data-testid="exercise-select"]', 'ssli_progression_0_0')
        self.page.select_option('[data-testid="progression-global-note-count"]', '3')
        ordered_fingers = self.page.evaluate("""() => {
          const targets = window.__exquisDebugSnapshot().exerciseEvents[0].targets
            .slice().sort((a, b) => a.midi - b.midi);
          return targets.map(target => {
            const key = document.querySelector(`.key.current-grip-target[data-cell-id="${target.cellId}"][data-midi="${target.midi}"]`);
            return key && key.querySelector('.chord-finger').textContent;
          });
        }""")
        self.assertEqual(ordered_fingers, ['2', '3', '4'], ordered_fingers)

    def test_regression_exquis_chord_fingers_use_contiguous_span_for_every_voicing_size(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.page.select_option('[data-testid="progression-genre-select"]', 'ssli-0')
        self.page.select_option('[data-testid="exercise-select"]', 'ssli_progression_0_0')
        expected = {
            '2': ['2', '3'],
            '3': ['2', '3', '4'],
            '4': ['1', '2', '3', '4'],
            '5': ['1', '2', '3', '4', '5'],
        }
        for note_count, expected_fingers in expected.items():
            self.page.select_option('[data-testid="progression-global-note-count"]', note_count)
            ordered_fingers = self.page.evaluate("""() => {
              const targets = window.__exquisDebugSnapshot().exerciseEvents[0].targets
                .slice().sort((a, b) => a.midi - b.midi);
              return targets.map(target => {
                const key = document.querySelector(`.key.current-grip-target[data-cell-id="${target.cellId}"][data-midi="${target.midi}"]`);
                return key && key.querySelector('.chord-finger').textContent;
              });
            }""")
            self.assertEqual(ordered_fingers, expected_fingers, {"noteCount": note_count, "fingers": ordered_fingers})

    def test_regression_repertoire_lessons_expose_named_loopable_sections(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'repertoire')
        options = self.page.locator('[data-testid="exercise-select"] option').all_text_contents()
        self.assertIn('Anthem progression', options)
        self.page.select_option('[data-testid="exercise-select"]', 'repertoire_anthem_progression')
        self.assertTrue(self.page.locator('[data-testid="repertoire-section-panel"]').is_visible())
        self.assertEqual(self.page.locator('[data-testid="repertoire-section-select"]').input_value(), 'verse')
        self.page.select_option('[data-testid="repertoire-section-select"]', 'chorus')
        self.page.locator('[data-testid="repertoire-tempo"]').fill('112')
        self.page.locator('[data-testid="repertoire-tempo"]').press('Tab')
        section = self.page.locator('[data-testid="repertoire-section-summary"]').inner_text()
        self.assertIn('Chorus', section)
        self.assertIn('112 BPM', section)
        self.assertIn('0 completed loops', section)
        self.page.locator('[data-testid="repertoire-count-in"]').click()
        self.assertIn('Count in: 1, 2, 3, 4.', self.page.locator('[data-testid="coach-feedback"]').inner_text())
        events = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents")
        self.assertEqual(len(events), 4, events)
        self.assertTrue(all(event["musicalIntent"].get("repertoireSection") == 'chorus' for event in events), events)
        self.page.evaluate("""() => {
          window.__mockRepertoireInput = { id: 'repertoire-exquis', name: 'Repertoire Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockRepertoireInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }""")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockRepertoireInput && window.__mockRepertoireInput.onmidimessage")
        self.page.evaluate("""async () => {
          const input = window.__mockRepertoireInput;
          const events = window.__exquisDebugSnapshot().exerciseEvents;
          for (const event of events) {
            for (const [index, target] of event.targets.entries()) {
              input.onmidimessage({ data: [0x90 | index, target.midi, 80] });
            }
            await new Promise((resolve) => setTimeout(resolve, 25));
          }
        }""")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"repertoire-section-summary\"]').textContent.includes('1 completed loop')")
        self.assertIn('1 completed loop', self.page.locator('[data-testid="repertoire-section-summary"]').inner_text())

    def test_regression_exercise_chooser_controls_remain_readable_at_desktop_width(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.page.locator('[data-testid="workspace-setup"]').click()
        controls = {
            "family": self.page.locator('[data-testid="exercise-family-select"]').bounding_box(),
            "genre": self.page.locator('[data-testid="progression-genre-select"]').bounding_box(),
            "exercise": self.page.locator('[data-testid="exercise-select"]').bounding_box(),
            "gripFingering": self.page.locator('[data-testid="grip-fingering-select"]').bounding_box()
        }
        self.assertGreaterEqual(controls["family"]["width"], 220, controls)
        self.assertGreaterEqual(controls["genre"]["width"], 220, controls)
        self.assertGreaterEqual(controls["exercise"]["width"], 450, controls)
        self.assertGreaterEqual(controls["gripFingering"]["width"], 220, controls)
        self.assertTrue(self.page.locator('[data-testid="progression-genre-control"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="octave-control"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="root-control"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="fingering-control"]').is_visible())
        self.assertEqual(self.page.locator('#practiceTitle').inner_text(), 'Progression lab')
        self.page.select_option('[data-testid="exercise-family-select"]', 'technique')
        self.page.locator('[data-testid="workspace-setup"]').click()
        self.assertTrue(self.page.locator('[data-testid="octave-control"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="root-control"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="fingering-control"]').is_visible())
        self.assertEqual(self.page.locator('#practiceTitle').inner_text(), 'Scale map')

    def test_regression_progression_lesson_presents_ii_v_i_in_order(self):
        self.page.select_option('[data-testid="exercise-select"]', "c_major_ii_v_i")
        events = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents")
        self.assertEqual([event["musicalIntent"]["degree"] for event in events], ["ii", "V", "I"], events)

    def test_regression_progression_prompt_includes_every_current_chord_member(self):
        self.page.select_option('[data-testid="exercise-select"]', "c_major_progression")
        self.assertEqual(self.page.evaluate("() => window.__exquisDebugPromptMidis()"), [48, 52, 55])

    def test_regression_exercise_control_does_not_overflow_header_at_desktop_viewport(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        overflow = self.page.evaluate("""() => Array.from(document.querySelectorAll('[data-testid="exercise-buttons"] .exercise-button'))
          .filter((button) => getComputedStyle(button).display !== 'none')
          .filter((button) => button.scrollWidth > button.clientWidth || button.scrollHeight > button.clientHeight)
          .map((button) => ({ text: button.textContent, width: button.clientWidth, scrollWidth: button.scrollWidth }))""")
        self.assertEqual(overflow, [], overflow)
        self.assertTrue(self.page.locator('[data-testid="exercise-select"]').is_visible())

    def test_regression_first_ssli_prompt_falls_back_until_preset_output_is_ready(self):
        decision = self.page.evaluate("""() => ({
          applyFailed: window.__exquisDebugShouldUseSsliPlayback(false, true),
          outputMissing: window.__exquisDebugShouldUseSsliPlayback(true, false),
          ready: window.__exquisDebugShouldUseSsliPlayback(true, true)
        })""")
        self.assertEqual(decision, {"applyFailed": False, "outputMissing": False, "ready": True})

    def test_regression_first_fallback_note_waits_for_audio_context_resume(self):
        events = self.page.evaluate("""async () => {
          const events = [];
          let resolveResume;
          const context = {
            state: 'suspended',
            resume: () => {
              events.push('resume');
              return new Promise((resolve) => { resolveResume = () => { context.state = 'running'; resolve(); }; });
            }
          };
          const playback = window.__exquisDebugStartAfterAudioResume(context, () => events.push('start'));
          events.push('before-resolve');
          resolveResume();
          await playback;
          return events;
        }""")
        self.assertEqual(events, ["resume", "before-resolve", "start"])

    def test_regression_progression_current_chord_highlights_every_target_button(self):
        self.page.select_option('[data-testid="exercise-family-select"]', "progressions")
        self.page.select_option('[data-testid="exercise-select"]', "c_major_progression")
        targets = self.page.locator('[data-testid="exquis-key"].current-grip-target')
        self.assertEqual(targets.count(), 3)
        self.assertEqual(sorted(targets.evaluate_all("elements => elements.map((element) => Number(element.dataset.midi))")), [48, 52, 55])
        self.assertTrue(all("chord target" in label for label in targets.evaluate_all("elements => elements.map((element) => element.getAttribute('aria-label'))")))
        self.assertEqual(self.page.locator('[data-testid="chord-target-bracket"]').count(), 0)
        self.assertEqual(targets.locator('.chord-target-hex-outline').count(), 0)
        self.assertTrue(all(name == "exquis-target-breathe" for name in targets.evaluate_all("elements => elements.map((element) => getComputedStyle(element).animationName)")))
        self.assertEqual(targets.locator('.finger.chord-finger').count(), 3)

    def test_regression_expressive_light_frame_is_root_relative_and_marks_every_chord_target(self):
        self.page.select_option('[data-testid="exercise-family-select"]', "progressions")
        self.page.select_option('[data-testid="exercise-select"]', "c_major_progression")
        frame = self.page.evaluate("() => window.__exquisLightDebug.currentFrame()")
        self.assertEqual(len(frame["pads"]), 61)
        self.assertEqual({pad["interval"] for pad in frame["pads"] if pad["isRoot"]}, {0})
        self.assertEqual({pad["hue"] for pad in frame["pads"] if pad["isRoot"]}, {120})
        major_hues = {
            interval: {pad["hue"] for pad in frame["pads"] if pad["interval"] == interval}
            for interval in [0, 2, 4, 5, 7, 9, 11]
        }
        self.assertEqual(major_hues, {0: {120}, 2: {171}, 4: {223}, 5: {274}, 7: {326}, 9: {17}, 11: {69}})
        targets = [pad for pad in frame["pads"] if pad["isTarget"]]
        self.assertEqual(sorted(pad["midi"] for pad in targets), [48, 52, 55])
        self.assertEqual({pad["midi"]: pad["hue"] for pad in targets}, {48: 120, 52: 223, 55: 326})
        self.assertTrue(all(pad["role"] == "target" for pad in targets))
        self.assertTrue(all(pad["isScale"] for pad in targets))
        hardware_frame = self.page.evaluate("() => window.__exquisLightDebug.hardwareFrame()")
        self.assertEqual(len(hardware_frame), 61)
        self.assertEqual({pad["paletteIndex"] for pad in hardware_frame if pad["role"] == "root"}, {28})
        self.assertEqual(
            {pad["midi"]: pad["paletteIndex"] for pad in hardware_frame if pad["isTarget"]},
            {48: 28, 52: 20, 55: 23}
        )
        root_rgb = self.page.evaluate("() => window.__exquisLightDebug.paletteRgbFor({ isRoot: true, interval: 0 })")
        scale_rgb = self.page.evaluate("() => window.__exquisLightDebug.paletteRgbFor({ isRoot: false, interval: 0 })")
        root_brightness = max(root_rgb)
        scale_brightness = max(scale_rgb)
        self.assertGreaterEqual(root_brightness, scale_brightness * 1.25)

        self.page.select_option('[data-testid="tonic-select"]', "5")
        shifted = self.page.evaluate("() => window.__exquisLightDebug.currentFrame()")
        self.assertEqual({pad["interval"] for pad in shifted["pads"] if pad["isRoot"]}, {0})
        self.assertEqual({pad["hue"] for pad in shifted["pads"] if pad["isRoot"]}, {120})
        self.assertNotEqual(
            next(pad["hue"] for pad in frame["pads"] if pad["pc"] == 0),
            next(pad["hue"] for pad in shifted["pads"] if pad["pc"] == 0),
        )

    def test_regression_c_minor_lights_only_the_meridian_duplicate_in_ui_and_hardware(self):
        self.page.select_option('[data-testid="tonic-select"]', '0')
        self.page.select_option('[data-testid="scale-select"]', 'aeolian')
        choices = self.page.evaluate("""() => {
          const frame = window.__exquisLightDebug.currentFrame().pads;
          const hardware = Object.fromEntries(window.__exquisLightDebug.hardwareFrame()
            .map((pad) => [pad.padId, pad.paletteIndex]));
          const keyById = Object.fromEntries([...document.querySelectorAll('[data-testid="exquis-key"]')]
            .map((key) => [key.dataset.cellId, key]));
          const keyboard = document.querySelector('[data-testid="keyboard"]').getBoundingClientRect();
          const center = { x: keyboard.left + keyboard.width / 2, y: keyboard.top + keyboard.height / 2 };
          const byMidi = frame.reduce((groups, pad) => {
            (groups[pad.midi] ||= []).push(pad);
            return groups;
          }, {});
          return Object.values(byMidi).map((pads) => {
            const candidates = pads.map((pad) => {
              const rect = keyById[pad.cellId].getBoundingClientRect();
              return {
                id: pad.cellId,
                midi: pad.midi,
                axisDistance: Math.abs(rect.top + rect.height / 2 - center.y),
                crossAxisDistance: Math.abs(rect.left + rect.width / 2 - center.x),
                frameLit: pad.isScale || pad.isRoot,
                hardwareLit: hardware[pad.padId] > 1,
                uiLit: keyById[pad.cellId].dataset.lightRole !== 'off'
              };
            }).sort((a, b) => a.axisDistance - b.axisDistance || a.crossAxisDistance - b.crossAxisDistance || a.id.localeCompare(b.id));
            return {
              midi: pads[0].midi,
              candidates,
              lit: candidates.filter((candidate) => candidate.frameLit),
              hardwareLit: candidates.filter((candidate) => candidate.hardwareLit),
              uiLit: candidates.filter((candidate) => candidate.uiLit)
            };
          }).filter((choice) => choice.candidates.length > 1 && choice.lit.length);
        }""")
        self.assertGreaterEqual(len(choices), 2, choices)
        for choice in choices:
            with self.subTest(midi=choice["midi"]):
                expected = choice["candidates"][0]["id"]
                self.assertEqual([candidate["id"] for candidate in choice["lit"]], [expected], choice)
                self.assertEqual([candidate["id"] for candidate in choice["hardwareLit"]], [expected], choice)
                self.assertEqual([candidate["id"] for candidate in choice["uiLit"]], [expected], choice)

    def test_regression_expressive_light_targets_pulse_without_hiding_interval_identity(self):
        self.page.select_option('[data-testid="exercise-family-select"]', "progressions")
        self.page.select_option('[data-testid="exercise-select"]', "c_major_progression")
        targets = self.page.locator('[data-testid="exquis-key"].current-grip-target')
        self.assertEqual(targets.count(), 3)
        self.assertTrue(all(role == "target" for role in targets.evaluate_all("elements => elements.map((element) => element.dataset.lightRole)")))
        self.assertTrue(all(interval is not None for interval in targets.evaluate_all("elements => elements.map((element) => element.dataset.interval)")))
        self.assertTrue(all(name == "exquis-target-breathe" for name in targets.evaluate_all("elements => elements.map((element) => getComputedStyle(element).animationName)")))
        self.assertTrue(all(float(duration.removesuffix("s")) == 1 for duration in targets.evaluate_all("elements => elements.map((element) => getComputedStyle(element).animationDuration)")))
        self.assertTrue(all(shadow == "none" for shadow in targets.evaluate_all("elements => elements.map((element) => getComputedStyle(element).boxShadow)")))
        self.assertTrue(all(filter_value != "none" for filter_value in targets.evaluate_all("elements => elements.map((element) => getComputedStyle(element).filter)")))

    def test_regression_expressive_light_reduced_motion_keeps_static_target_emphasis(self):
        self.page.emulate_media(reduced_motion="reduce")
        self.page.select_option('[data-testid="exercise-family-select"]', "progressions")
        self.page.select_option('[data-testid="exercise-select"]', "c_major_progression")
        targets = self.page.locator('[data-testid="exquis-key"].current-grip-target')
        self.assertEqual(targets.count(), 3)
        self.assertTrue(all(name == "none" for name in targets.evaluate_all("elements => elements.map((element) => getComputedStyle(element).animationName)")))
        self.assertTrue(all(filter_value != "none" for filter_value in targets.evaluate_all("elements => elements.map((element) => getComputedStyle(element).filter)")))

    def test_regression_illuminated_pad_labels_have_minimum_contrast(self):
        self.page.select_option('[data-testid="exercise-family-select"]', "progressions")
        self.page.select_option('[data-testid="exercise-select"]', "c_major_progression")
        self.page.locator('[data-testid="workspace-practice"]').click()
        pads = self.page.evaluate("""() => {
          const parseColor = (value) => {
            const values = (value.match(/\\d+(?:\\.\\d+)?/g) || []).slice(0, 3).map(Number);
            return value.startsWith('color(') ? values.map((component) => component * 255) : values;
          };
          const linear = (component) => component <= 0.04045
            ? component / 12.92 : Math.pow((component + 0.055) / 1.055, 2.4);
          const luminance = (rgb) => 0.2126 * linear(rgb[0] / 255)
            + 0.7152 * linear(rgb[1] / 255) + 0.0722 * linear(rgb[2] / 255);
          const pads = [...document.querySelectorAll('[data-testid="exquis-key"].hardware-lit')];
          const states = ['', 'midi-hit', 'midi-held', 'midi-held-pitch', 'midi-pitch', 'midi-last', 'midi-last-pitch', 'mismatch', 'dimmed'];
          return states.flatMap((state) => pads.map((element) => {
            if (state) element.classList.add(state);
            const buttonStyle = getComputedStyle(element);
            const labels = ['.note', '.octave'].map((selector) => {
              const labelStyle = getComputedStyle(element.querySelector(selector));
              const foreground = parseColor(labelStyle.color);
              const background = parseColor(buttonStyle.backgroundColor);
              const foregroundLuminance = luminance(foreground);
              const backgroundLuminance = luminance(background);
              return {
                selector,
                foreground: labelStyle.color,
                contrast: (Math.max(foregroundLuminance, backgroundLuminance) + 0.05)
                  / (Math.min(foregroundLuminance, backgroundLuminance) + 0.05)
              };
            });
            const result = { state: state || 'base', note: element.querySelector('.note').textContent.trim(), background: buttonStyle.backgroundColor, labels };
            if (state) element.classList.remove(state);
            return result;
          }));
        }""")
        self.assertTrue(pads)
        baseline_backgrounds = {pad["note"]: pad["background"] for pad in pads if pad["state"] == "base"}
        self.assertTrue(all(pad["background"] == baseline_backgrounds[pad["note"]] for pad in pads), pads)
        labels = [label for pad in pads for label in pad["labels"]]
        self.assertTrue(all(label["foreground"] in {"rgb(11, 16, 22)", "rgb(23, 25, 28)"} for label in labels), pads)
        self.assertGreaterEqual(min(label["contrast"] for label in labels), 4.5, pads)

    def test_regression_root_marker_is_visible_without_relying_on_hue(self):
        roots = self.page.locator('[data-testid="exquis-key"].tonic')
        self.assertGreater(roots.count(), 0)
        self.assertEqual(roots.locator('.root-marker').count(), roots.count())
        self.assertTrue(all(marker == "R" for marker in roots.locator('.root-marker').all_text_contents()))

    def test_major_third_exercise_emits_selected_root_interval(self):
        self.page.select_option('[data-testid="exercise-select"]', "major_third")
        event = self.page.evaluate("() => window.__exquisDebugSnapshot().exerciseEvents[0]")
        self.assertEqual(event["type"], "grip", event)
        self.assertEqual([target["midi"] for target in event["targets"]], [48, 52], event)
        self.assertTrue(event["valid"], event)

    def test_major_triad_midi_grip_scores_once_and_advances_once(self):
        self.page.select_option('[data-testid="exercise-select"]', "major_triad")
        self.page.select_option('[data-testid="grip-fingering-select"]', "compact")
        target_fingers = self.page.locator('[data-testid="target-finger"]').text_content()
        self.assertIn("Pinky", target_fingers)
        self.assertIn("Thumb", target_fingers)
        self.page.evaluate("""() => {
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockExquisInput) }, outputs: { forEach: () => {} }, onstatechange: null
          });
        }""")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        for raw, channel in [(48, 0), (52, 1), (55, 2)]:
            self.page.evaluate("(args) => window.__mockExquisInput.onmidimessage({ data: [0x90 | args.channel, args.raw, 80] })", {"raw": raw, "channel": channel})
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-feedback\"]').textContent.includes('Correct grip')")
        self.assertIn("Declared Compact 5-3-1 fingering", self.page.locator('[data-testid="coach-feedback"]').inner_text())
        self.assertIn("Score: 1 correct / 0 missed", self.page.locator('[data-testid="drill-score"]').inner_text())
        self.assertEqual(self.page.locator('[data-testid="step-readout"]').inner_text(), "1 / 1")

    def test_major_triad_partial_grip_does_not_advance(self):
        self.page.select_option('[data-testid="exercise-select"]', "major_triad")
        self.page.evaluate("""() => {
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({ inputs: { forEach: (cb) => cb(window.__mockExquisInput) }, outputs: { forEach: () => {} }, onstatechange: null });
        }""")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90, 48, 80] })")
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-feedback\"]').textContent.includes('Grip not accepted')")
        self.assertIn("missing E3 + G3", self.page.locator('[data-testid="coach-feedback"]').inner_text())
        self.assertIn("Score: 0 correct / 1 missed", self.page.locator('[data-testid="drill-score"]').inner_text())
        self.assertEqual(self.page.locator('[data-testid="step-readout"]').inner_text(), "1 / 1")

    def test_major_triad_late_grip_does_not_advance(self):
        self.page.select_option('[data-testid="exercise-select"]', "major_triad")
        self.page.evaluate("""() => {
          window.__mockExquisInput = { id: 'exquis-usb', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({ inputs: { forEach: (cb) => cb(window.__mockExquisInput) }, outputs: { forEach: () => {} }, onstatechange: null });
        }""")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x90, 48, 80] })")
        self.page.wait_for_timeout(100)
        for raw, channel in [(52, 1), (55, 2)]:
            self.page.evaluate("(args) => window.__mockExquisInput.onmidimessage({ data: [0x90 | args.channel, args.raw, 80] })", {"raw": raw, "channel": channel})
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-feedback\"]').textContent.includes('played too far apart')")
        self.assertIn("Score: 0 correct / 1 missed", self.page.locator('[data-testid="drill-score"]').inner_text())

    def test_regression_migrated_scale_paths_preserve_order(self):
        for exercise_id in ["root_octave", "two_octaves", "inner_ladder", "root_returns"]:
            self.page.select_option('[data-testid="exercise-select"]', exercise_id)
            snapshot = self.page.evaluate("() => window.__exquisDebugSnapshot()")
            path_midis = [step["midi"] for step in snapshot["currentPath"]]
            event_midis = [event["targets"][0]["midi"] for event in snapshot["exerciseEvents"]]
            self.assertEqual(event_midis, path_midis, (exercise_id, snapshot))
            self.assertTrue(all(event["type"] == "note" and event["valid"] for event in snapshot["exerciseEvents"]), snapshot)

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
        self.assertTrue(self.page.locator('[data-testid="practice-coach"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="practice-target-panel"]').is_visible())
        self.page.locator('[data-testid="play-mode"]').click()
        for test_id in [
            "root-control",
            "hand-control",
            "exercise-control",
            "fingering-control",
            "view-control",
            "practice-stepper",
            "drill-section",
            "practice-path-strip",
        ]:
            self.assertFalse(self.page.locator(f'[data-testid="{test_id}"]').is_visible(), test_id)
        self.assertTrue(self.page.locator('[data-testid="practice-coach"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="sound-engine-select"]').is_visible())
        self.open_audio_drawer()
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
        order = self.page.evaluate("""() => [
          ...document.querySelector('.controls-grid').children,
          ...document.querySelector('.practice-workflow-controls').children
        ].map((el) => (
          el.getAttribute('data-testid') || el.querySelector('[data-testid]')?.getAttribute('data-testid') || ''
        ))""")
        self.assertEqual(order, [
            "mode-switch",
            "tonic-select",
            "scale-select",
            "octave-control",
            "root-control",
            "hand-control",
            "exercise-family-control",
            "progression-genre-control",
            "exercise-control",
            "fingering-control",
            "grip-fingering-control",
            "harmony-triad-controls",
            "view-control",
        ])
        header_text = self.page.locator(".top-panel").inner_text()
        self.assertIn("Session", header_text)
        self.assertIn("Root Octave", header_text)
        self.assertIn("Start Button", header_text)
        self.assertIn("Finger Pattern", header_text)
        self.assertIn("Surface", header_text)

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

    def test_regression_midi_coach_activity_lists_all_currently_held_notes(self):
        self.page.evaluate("""
        () => {
          window.__mockCoachInput = { id: 'coach-held-exquis', name: 'Coach Held Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__mockCoachInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="play-mode"]').click()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockCoachInput && window.__mockCoachInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockCoachInput.onmidimessage({ data: [0x91, 48, 80] });
          window.__mockCoachInput.onmidimessage({ data: [0x92, 52, 84] });
          window.__mockCoachInput.onmidimessage({ data: [0x93, 55, 88] });
          window.__mockCoachInput.onmidimessage({ data: [0xA2, 52, 127] });
        }
        """)
        self.page.wait_for_function("""() => {
          const text = document.querySelector('[data-testid="midi-activity"]').textContent;
          return text.includes('Activity: poly-aftertouch E3 pressure 127') && text.includes('Held: C3 p80, E3 p127, G3 p88');
        }""")
        activity = self.page.locator('[data-testid="midi-activity"]').inner_text()
        self.assertIn("Activity: poly-aftertouch E3 pressure 127", activity)
        self.assertIn("Held: C3 p80, E3 p127, G3 p88", activity)
        self.page.evaluate("""
        () => {
          window.__mockCoachInput.onmidimessage({ data: [0xA1, 48, 22] });
          window.__mockCoachInput.onmidimessage({ data: [0xA3, 55, 101] });
        }
        """)
        self.page.wait_for_function("""() => {
          const text = document.querySelector('[data-testid="midi-activity"]').textContent;
          return text.includes('Held: C3 p22, E3 p127, G3 p101');
        }""")
        self.page.evaluate("() => window.__mockCoachInput.onmidimessage({ data: [0x82, 52, 0] })")
        self.page.wait_for_function("""() => {
          const text = document.querySelector('[data-testid="midi-activity"]').textContent;
          return text.includes('Held: C3 p22, G3 p101') && !text.includes('E3 p127');
        }""")

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
        self.open_hardware_tools()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="sync-exquis"]').click()
        self.page.select_option('[data-testid="tonic-select"]', "5")
        self.page.select_option('[data-testid="scale-select"]', "dorian")
        self.page.wait_for_timeout(2400)
        sent = self.page.evaluate("() => window.__mockExquisOutput.sent")
        self.assertEqual(self.page.evaluate("() => window.__sysexRequests[0].sysex"), True)
        self.assertIn([176, 122, 0], sent)
        self.assertIn([176, 120, 0], sent)
        self.assertIn([176, 123, 0], sent)
        self.assertIn([191, 122, 0], sent)
        self.assertIn([240, 0, 33, 126, 127, 0, 1, 247], sent)
        self.assertNotIn([240, 0, 33, 126, 127, 0, 17, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 6, 5, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 1, 1, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 7, 0, 247], sent)
        self.assertNotIn([240, 0, 33, 126, 127, 1, 8, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 8, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 247], sent)
        palette_messages = [message for message in sent if len(message) > 6 and message[:6] == [240, 0, 33, 126, 127, 2]]
        self.assertTrue(any(message[6] == 1 and len(message) == 92 for message in palette_messages))
        self.assertEqual(sum(1 for message in sent if len(message) == 3 and message[0] == 191 and 0 <= message[1] < 61 and (message[2] == 1 or 16 <= message[2] <= 28)), 61)
        self.assertIn([240, 0, 33, 126, 127, 3, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 6, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 7, 247], sent)
        transaction_start = max(index for index, message in enumerate(sent) if message == [240, 0, 33, 126, 127, 0, 1, 247])
        transaction = sent[transaction_start:]
        self.assertNotIn([240, 0, 33, 126, 127, 6, 0, 247], transaction)
        self.assertLess(transaction.index([240, 0, 33, 126, 127, 6, 5, 247]), transaction.index([240, 0, 33, 126, 127, 1, 1, 247]))
        self.assertLess(transaction.index([240, 0, 33, 126, 127, 1, 1, 247]), transaction.index([240, 0, 33, 126, 127, 7, 0, 247]))
        self.assertLess(transaction.index([240, 0, 33, 126, 127, 7, 0, 247]), transaction.index([240, 0, 33, 126, 127, 8, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 247]))
        self.assertLess(transaction.index([240, 0, 33, 126, 127, 8, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 247]), transaction.index([240, 0, 33, 126, 127, 3, 247]))
        last_led_index = max(index for index, message in enumerate(transaction) if len(message) == 3 and message[0] == 191 and 0 <= message[1] < 61 and (message[2] == 1 or 16 <= message[2] <= 28))
        palette_index = next(index for index, message in enumerate(transaction) if len(message) > 6 and message[:6] == [240, 0, 33, 126, 127, 2])
        self.assertLess(transaction.index([240, 0, 33, 126, 127, 3, 247]), palette_index)
        self.assertLess(palette_index, last_led_index)
        self.assertLess(last_led_index, transaction.index([240, 0, 33, 126, 127, 6, 247]))
        self.assertLess(transaction.index([240, 0, 33, 126, 127, 6, 247]), transaction.index([240, 0, 33, 126, 127, 7, 247]))
        self.assertNotIn([240, 0, 33, 126, 127, 0, 0, 247], transaction)
        self.assertIn([240, 0, 33, 126, 247], sent)
        self.assertNotIn([240, 0, 33, 126, 4, 2, 29, 247], sent)
        self.assertNotIn([240, 0, 33, 126, 7, 2, 127, 95, 63, 247], sent)
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0xF0, 0x00, 0x21, 0x7E, 0xF7] })")
        echo_count = self.page.evaluate("() => window.__mockExquisOutput.sent.length")
        self.page.wait_for_timeout(140)
        post_input_messages = self.page.evaluate("(before) => window.__mockExquisOutput.sent.slice(before)", echo_count)
        self.assertEqual(
            [message for message in post_input_messages if message not in ([254], [240, 0, 33, 126, 247])],
            []
        )
        self.page.locator('[data-testid="advanced-hardware-research"]').evaluate("element => element.open = true")
        self.page.locator('[data-testid="legacy-map-select"]').select_option("top_left")
        self.page.wait_for_timeout(60)
        remapped = self.page.evaluate("(before) => window.__mockExquisOutput.sent.slice(before)", echo_count)
        self.assertIn([240, 0, 33, 126, 4, 0, 62, 247], remapped)
        before_lights = self.page.evaluate("() => window.__mockExquisOutput.sent.length")
        self.page.locator('[data-testid="legacy-light-select"]').select_option("both")
        self.page.wait_for_timeout(60)
        light_messages = self.page.evaluate("(before) => window.__mockExquisOutput.sent.slice(before)", before_lights)
        self.assertIn([240, 0, 33, 126, 3, 3, 127, 95, 63, 247], light_messages)
        self.assertIn([240, 0, 33, 126, 7, 3, 127, 95, 63, 247], light_messages)
        self.open_audio_drawer()
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("Exquis legacy key/mode", log)
        self.assertIn("buttonColors=61 noteColors=0 noteMap=61", log)
        self.assertIn("custom-scale=dorian", log)
        self.page.locator('[data-testid="sync-exquis"]').click()
        self.assertIn([240, 0, 33, 126, 127, 0, 0, 247], self.page.evaluate("() => window.__mockExquisOutput.sent"))

    def test_regression_exquis_sync_pulses_current_targets_and_clears_prior_targets(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          window.__mockExquisOutput = {
            id: 'exquis-out', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', sent: [],
            send(bytes) { this.sent.push([...bytes]); }
          };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (callback) => callback(window.__mockExquisInput) },
            outputs: { forEach: (callback) => callback(window.__mockExquisOutput) },
            onstatechange: null
          });
        }
        """)
        self.page.select_option('[data-testid="exercise-family-select"]', "technique")
        self.page.select_option('[data-testid="exercise-select"]', "root_octave")
        self.open_hardware_tools()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="sync-exquis"]').click()
        self.page.wait_for_timeout(2200)
        self.page.locator('[data-testid="workspace-practice"]').click()
        self.page.wait_for_timeout(300)
        targets_before = self.page.evaluate("() => window.__exquisLightDebug.hardwareFrame().filter((pad) => pad.isTarget).map((pad) => pad.padId)")
        self.assertEqual(len(targets_before), 1)
        sent = self.page.evaluate("() => window.__mockExquisOutput.sent")
        for pad_id in targets_before:
            self.assertIn([175, pad_id, 63], sent)

        before_advance = len(sent)
        self.page.locator('[data-testid="next-step"]').click()
        targets_after = self.page.evaluate("() => window.__exquisLightDebug.hardwareFrame().filter((pad) => pad.isTarget).map((pad) => pad.padId)")
        self.assertNotEqual(targets_after, targets_before)
        self.page.wait_for_timeout(1000)
        updates = self.page.evaluate("(count) => window.__mockExquisOutput.sent.slice(count)", before_advance)
        for pad_id in targets_before:
            self.assertIn([175, pad_id, 0], updates)
        for pad_id in targets_after:
            self.assertIn([175, pad_id, 63], updates)

    def test_regression_exquis_sync_advances_target_pulse_after_correct_sequence_note(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          window.__mockExquisOutput = {
            id: 'exquis-out', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', sent: [],
            send(bytes) { this.sent.push([...bytes]); }
          };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (callback) => callback(window.__mockExquisInput) },
            outputs: { forEach: (callback) => callback(window.__mockExquisOutput) },
            onstatechange: null
          });
        }
        """)
        self.page.select_option('[data-testid="exercise-family-select"]', "technique")
        self.page.select_option('[data-testid="exercise-select"]', "root_octave")
        self.open_hardware_tools()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="sync-exquis"]').click()
        self.page.wait_for_timeout(2200)
        before = self.page.evaluate("""() => ({
          target: window.__exquisLightDebug.hardwareFrame().find((pad) => pad.isTarget),
          sent: window.__mockExquisOutput.sent.length
        })""")
        self.assertIsNotNone(before["target"])
        self.page.evaluate("(midi) => window.__mockExquisInput.onmidimessage({ data: [0x90, midi, 100] })", before["target"]["midi"])
        self.page.wait_for_timeout(1000)
        after = self.page.evaluate("""(count) => ({
          target: window.__exquisLightDebug.hardwareFrame().find((pad) => pad.isTarget),
          updates: window.__mockExquisOutput.sent.slice(count)
        })""", before["sent"])
        self.assertIsNotNone(after["target"])
        self.assertNotEqual(after["target"]["padId"], before["target"]["padId"])
        self.assertIn([175, before["target"]["padId"], 0], after["updates"])
        self.assertIn([175, after["target"]["padId"], 63], after["updates"])

    def test_regression_practice_notation_lens_tracks_step_and_conceals_ear_answers(self):
        panel = self.page.locator('[data-testid="practice-notation"]')
        staff = self.page.locator('[data-testid="staff-notation"]')
        roll = self.page.locator('[data-testid="piano-roll-notation"]')
        self.assertTrue(panel.is_visible())
        self.assertTrue(staff.is_visible())
        self.assertTrue(roll.is_visible())
        active_before = self.page.locator('[data-testid="piano-roll-note"].notation-active')
        self.assertEqual(active_before.count(), 1)
        before_index = active_before.get_attribute('data-event-index')
        before_midi = active_before.get_attribute('data-midi')
        self.page.locator('[data-testid="next-step"]').click()
        active_after = self.page.locator('[data-testid="piano-roll-note"].notation-active')
        self.assertEqual(active_after.count(), 1)
        self.assertNotEqual(active_after.get_attribute('data-event-index'), before_index)
        self.assertNotEqual(active_after.get_attribute('data-midi'), before_midi)
        self.assertEqual(self.page.locator('[data-testid="staff-note"].notation-active').count(), 1)
        self.page.select_option('[data-testid="exercise-family-select"]', 'ear')
        self.page.select_option('[data-testid="exercise-select"]', 'ear_major_third')
        self.assertTrue(self.page.locator('[data-testid="notation-concealed"]').is_visible())
        self.assertEqual(self.page.locator('[data-testid="piano-roll-note"]').count(), 0)
        self.assertEqual(self.page.locator('[data-testid="staff-note"]').count(), 0)

    def test_practice_notation_lens_stacks_canonical_grip_pitches(self):
        self.page.select_option('[data-testid="exercise-family-select"]', 'progressions')
        self.page.select_option('[data-testid="exercise-select"]', 'c_major_progression')
        roll_notes = self.page.locator('[data-testid="piano-roll-note"].notation-active')
        staff_notes = self.page.locator('[data-testid="staff-note"].notation-active')
        self.assertEqual(roll_notes.count(), 3)
        self.assertEqual(staff_notes.count(), 3)
        roll_midis = sorted(int(roll_notes.nth(index).get_attribute('data-midi')) for index in range(roll_notes.count()))
        staff_midis = sorted(int(staff_notes.nth(index).get_attribute('data-midi')) for index in range(staff_notes.count()))
        self.assertEqual(roll_midis, staff_midis)
        self.assertEqual(len(set(roll_notes.evaluate_all("nodes => nodes.map((node) => node.getAttribute('data-event-index'))"))), 1)

    def test_practice_notation_uses_music_symbols_and_keeps_a_compact_tablet_fit(self):
        self.page.set_viewport_size({"width": 768, "height": 1024})
        self.page.select_option('[data-testid="tonic-select"]', '4')  # E major: four sharps.
        panel = self.page.locator('[data-testid="practice-notation"]')
        staff = self.page.locator('[data-testid="staff-notation"]')
        roll = self.page.locator('[data-testid="piano-roll-notation"]')
        panel_box = panel.bounding_box()
        staff_box = staff.bounding_box()
        roll_box = roll.bounding_box()
        self.assertLessEqual(panel_box['height'], 116)
        self.assertLess(abs(staff_box['y'] - roll_box['y']), 2, 'tablet keeps staff and piano roll side by side')
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 768)
        symbols = staff.locator('text').all_text_contents()
        self.assertTrue(any(symbol in {'\U0001d11e', '\U0001d122'} for symbol in symbols))
        self.assertEqual(staff.locator('.key-signature-accidental').count(), 4)
        self.assertIn('E Major', staff.get_attribute('aria-label'))

    def test_regression_exquis_sync_pulses_every_current_chord_target(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          window.__mockExquisOutput = {
            id: 'exquis-out', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', sent: [],
            send(bytes) { this.sent.push([...bytes]); }
          };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (callback) => callback(window.__mockExquisInput) },
            outputs: { forEach: (callback) => callback(window.__mockExquisOutput) },
            onstatechange: null
          });
        }
        """)
        self.page.select_option('[data-testid="exercise-family-select"]', "progressions")
        self.page.select_option('[data-testid="exercise-select"]', "c_major_progression")
        self.open_hardware_tools()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="sync-exquis"]').click()
        self.page.wait_for_timeout(2200)
        self.page.locator('[data-testid="workspace-practice"]').click()
        self.page.wait_for_timeout(300)
        chord_targets = self.page.evaluate("() => window.__exquisLightDebug.hardwareFrame().filter((pad) => pad.isTarget).map((pad) => pad.padId)")
        self.assertEqual(len(chord_targets), 3)
        sent = self.page.evaluate("() => window.__mockExquisOutput.sent")
        for pad_id in chord_targets:
            self.assertIn([175, pad_id, 63], sent)

    def test_regression_exquis_rgb_pad_probe_uses_official_pad_only_direct_led_protocol(self):
        self.page.evaluate("""
        () => {
          window.__mockExquisInput = { id: 'exquis-in', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          window.__mockExquisOutput = {
            id: 'exquis-out', name: 'Exquis USB MIDI', manufacturer: 'Intuitive Instruments', sent: [],
            send(bytes) { this.sent.push([...bytes]); }
          };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (callback) => callback(window.__mockExquisInput) },
            outputs: { forEach: (callback) => callback(window.__mockExquisOutput) },
            onstatechange: null
          });
        }
        """)
        self.open_hardware_tools()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="advanced-hardware-research"] summary').click()
        before = self.page.evaluate("() => window.__mockExquisOutput.sent.length")
        self.page.locator('[data-testid="rgb-pad-test-exquis"]').click()
        self.page.wait_for_timeout(360)
        sent = self.page.evaluate("(count) => window.__mockExquisOutput.sent.slice(count)", before)
        self.assertIn([240, 0, 33, 126, 127, 0, 1, 247], sent)
        self.assertIn([240, 0, 33, 126, 127, 4, 0, 127, 0, 127, 0, 247], sent)
        self.assertFalse(any(message[:4] == [240, 0, 33, 126] and message[4] != 127 for message in sent))
        self.assertNotIn([240, 0, 33, 126, 127, 0, 16, 247], sent)
        self.assertNotIn([191, 100, 127], sent)
        self.assertIn("Official pad color test active: bottom-left pad is magenta", self.page.locator('[data-testid="exquis-sync-status"]').inner_text())

    def test_regression_manual_key_mode_change_syncs_after_hardware_readback(self):
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
            inputs: { forEach: (callback) => callback(window.__mockExquisInput) },
            outputs: { forEach: (callback) => callback(window.__mockExquisOutput) },
            onstatechange: null
          });
        }
        """)
        self.open_hardware_tools()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.locator('[data-testid="sync-exquis"]').click()
        self.page.wait_for_timeout(1200)
        sent_before_change = self.page.evaluate("() => window.__mockExquisOutput.sent.length")

        self.page.select_option('[data-testid="tonic-select"]', "5")
        self.page.select_option('[data-testid="scale-select"]', "dorian")
        self.page.evaluate("""() => window.__mockExquisInput.onmidimessage({
          data: [0xF0, 0x00, 0x21, 0x7E, 0x7F, 0x06, 0x00, 0xF7]
        })""")
        self.page.wait_for_timeout(1200)
        sent_after_change = self.page.evaluate("(count) => window.__mockExquisOutput.sent.slice(count)", sent_before_change)
        self.assertEqual(self.page.locator('[data-testid="tonic-select"]').input_value(), "5")
        self.assertIn([240, 0, 33, 126, 127, 6, 5, 247], sent_after_change)
        self.assertIn([240, 0, 33, 126, 127, 8, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 247], sent_after_change)

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
        self.open_hardware_tools()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.select_option('[data-testid="tonic-select"]', "5")
        self.page.select_option('[data-testid="scale-select"]', "dorian")
        self.page.locator('[data-testid="advanced-hardware-research"] summary').click()
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
        self.page.locator('[data-testid="hardware-diagnostics"]').click()
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

    def test_regression_studio_diagnostics_opens_visible_hardware_drawer(self):
        self.open_hardware_tools()
        hardware = self.page.locator('[data-testid="hardware-tools"]')
        self.assertTrue(hardware.is_visible())
        self.assertFalse(hardware.locator('> summary').is_visible())
        advanced = self.page.locator('[data-testid="advanced-hardware-research"]')
        self.assertTrue(advanced.is_visible())
        self.assertFalse(advanced.evaluate("element => element.open"))
        advanced.locator('summary').click()
        self.assertEqual(self.page.locator('[data-testid="native-probe-exquis"]').inner_text(), "Native LED Probe")
        self.page.locator('[data-testid="hardware-diagnostics"]').click()
        drawer = self.page.locator('[data-testid="console-panel"]')
        log = self.page.locator('[data-testid="diagnostic-log"]')
        drawer_box = drawer.bounding_box()
        log_box = log.bounding_box()
        self.assertTrue(drawer.is_visible())
        self.assertTrue(log.is_visible())
        self.assertIsNotNone(drawer_box)
        self.assertIsNotNone(log_box)
        self.assertGreater(drawer_box["width"], 300)
        self.assertGreater(drawer_box["height"], 180)
        self.assertGreater(log_box["height"], 160)
        drawer_layout = drawer.evaluate("""element => ({
          position: getComputedStyle(element).position,
          left: element.getBoundingClientRect().left,
          hardwareRight: document.querySelector('[data-testid="hardware-tools"]').getBoundingClientRect().right,
          actionLabels: [...element.querySelectorAll('.console-actions button')].map(button => button.textContent.trim()),
          clippedActions: [...element.querySelectorAll('.console-actions button')].filter(button => button.scrollWidth > button.clientWidth).map(button => button.textContent.trim())
        })""")
        self.assertEqual(drawer_layout["position"], "absolute")
        self.assertLess(drawer_layout["left"], drawer_layout["hardwareRight"])
        self.assertEqual(drawer_layout["actionLabels"], ["Audio snapshot", "Clear log", "Copy", "Collapse"])
        self.assertEqual(drawer_layout["clippedActions"], [])
        self.assertEqual(self.page.locator('[data-testid="probe-exquis"]').inner_text(), "Protocol Discovery Probe")
        labels = advanced.locator('label').evaluate_all("elements => elements.map((element) => element.querySelector('span').textContent.trim())")
        self.assertIn("Legacy pad-map origin", labels)
        self.assertIn("Legacy light destination", labels)
        self.assertIn("experimental or disruptive MIDI messages", advanced.inner_text())
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

    def test_regression_studio_hardware_fits_laptop_height_without_scroll_or_cutoff(self):
        self.page.set_viewport_size({"width": 1280, "height": 600})
        self.open_hardware_tools()

        def layout_metrics():
            return self.page.evaluate("""() => {
              const rect = (selector) => document.querySelector(selector).getBoundingClientRect().toJSON();
              const studio = document.querySelector('[data-testid="studio-workspace"]');
              const slot = document.querySelector('#studioControlsSlot');
              return {
                studio: rect('[data-testid="studio-workspace"]'),
                hardware: rect('[data-testid="hardware-tools"]'),
                activity: rect('[data-testid="midi-activity"]'),
                console: rect('[data-testid="console-panel"]'),
                studioScrollHeight: studio.scrollHeight,
                studioClientHeight: studio.clientHeight,
                slotScrollHeight: slot.scrollHeight,
                slotClientHeight: slot.clientHeight
              };
            }""")

        collapsed = layout_metrics()
        self.assertLessEqual(collapsed["hardware"]["bottom"], collapsed["studio"]["bottom"])
        self.assertLessEqual(collapsed["activity"]["bottom"], collapsed["hardware"]["bottom"])
        self.assertLessEqual(collapsed["studioScrollHeight"], collapsed["studioClientHeight"] + 1)
        self.assertLessEqual(collapsed["slotScrollHeight"], collapsed["slotClientHeight"] + 1)
        density = self.page.evaluate("""() => {
          const hardware = document.querySelector('[data-testid="hardware-tools"]').getBoundingClientRect();
          const regions = [...document.querySelectorAll(
            '[aria-labelledby="hardware-connection-heading"], [aria-labelledby="hardware-diagnostics-heading"], .advanced-hardware-research, #exquisSyncStatus, #midiActivity'
          )].map((element) => element.getBoundingClientRect());
          const columns = 20;
          const rows = 12;
          const occupied = [];
          for (let row = 0; row < rows; row += 1) {
            for (let column = 0; column < columns; column += 1) {
              const cell = {
                left: hardware.left + column * hardware.width / columns,
                right: hardware.left + (column + 1) * hardware.width / columns,
                top: hardware.top + row * hardware.height / rows,
                bottom: hardware.top + (row + 1) * hardware.height / rows
              };
              occupied[row * columns + column] = regions.some((region) => (
                region.left < cell.right && region.right > cell.left &&
                region.top < cell.bottom && region.bottom > cell.top
              ));
            }
          }
          let largestEmptyCells = 0;
          for (let top = 0; top < rows; top += 1) {
            for (let bottom = top; bottom < rows; bottom += 1) {
              for (let left = 0; left < columns; left += 1) {
                for (let right = left; right < columns; right += 1) {
                  let empty = true;
                  for (let row = top; row <= bottom && empty; row += 1) {
                    for (let column = left; column <= right; column += 1) {
                      if (occupied[row * columns + column]) {
                        empty = false;
                        break;
                      }
                    }
                  }
                  if (empty) largestEmptyCells = Math.max(largestEmptyCells, (right - left + 1) * (bottom - top + 1));
                }
              }
            }
          }
          return {
            occupiedRatio: occupied.filter(Boolean).length / (columns * rows),
            largestEmptyRatio: largestEmptyCells / (columns * rows)
          };
        }""")
        self.assertGreaterEqual(density["occupiedRatio"], 0.70, density)
        self.assertLessEqual(density["largestEmptyRatio"], 0.16, density)

        self.page.locator('[data-testid="hardware-diagnostics"]').click()
        expanded = layout_metrics()
        self.assertLessEqual(expanded["hardware"]["bottom"], expanded["studio"]["bottom"])
        self.assertLessEqual(expanded["activity"]["bottom"], expanded["hardware"]["bottom"])
        self.assertLessEqual(expanded["console"]["bottom"], expanded["hardware"]["bottom"])
        self.assertGreaterEqual(expanded["console"]["left"], expanded["activity"]["right"])
        self.assertLessEqual(expanded["studioScrollHeight"], expanded["studioClientHeight"] + 1)
        self.assertLessEqual(expanded["slotScrollHeight"], expanded["slotClientHeight"] + 1)

    def test_regression_exquis_edge_controls_follow_orientation_layout(self):
        def metrics_for(orientation):
            self.page.select_option('[data-testid="orientation-select"]', orientation)
            self.page.wait_for_timeout(80)
            return self.page.evaluate("""() => {
              const box = (sel) => document.querySelector(sel).getBoundingClientRect();
              const consolePanel = document.querySelector('[data-testid="console-panel"]');
              const consoleBox = consolePanel.getBoundingClientRect();
              const consoleSafeTop = getComputedStyle(consolePanel).position === 'fixed' && consoleBox.width && consoleBox.height
                ? consolePanel.getBoundingClientRect().top
                : window.innerHeight;
              const build = document.querySelector('[data-testid="build-version"]');
              const buildSafeTop = getComputedStyle(build).position === 'fixed'
                ? build.getBoundingClientRect().top
                : window.innerHeight;
              const safeTop = Math.min(
                window.innerHeight,
                consoleSafeTop,
                buildSafeTop
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
        if horizontal["top"]["width"] and horizontal["bottom"]["width"]:
            self.assertLess(horizontal["bottom"]["right"], horizontal["keyboard"]["left"], horizontal)
            self.assertGreater(horizontal["top"]["left"], horizontal["keyboard"]["right"], horizontal)
            self.assertGreaterEqual(horizontal["top"]["width"], 118, horizontal)
            self.assertGreaterEqual(horizontal["bottom"]["width"], 72, horizontal)
            self.assertLessEqual(horizontal["bottom"]["width"], 92, horizontal)
            self.assertLess(abs((horizontal["top"]["top"] + horizontal["top"]["bottom"]) / 2 - (horizontal["keyboard"]["top"] + horizontal["keyboard"]["bottom"]) / 2), horizontal["keyboard"]["height"] * 0.28, horizontal)
        else:
            self.assertGreater(horizontal["keyboard"]["width"], 0, horizontal)

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
                  const consolePanel = document.querySelector('[data-testid="console-panel"]');
                  const consoleBox = consolePanel.getBoundingClientRect();
                  const consoleSafeTop = getComputedStyle(consolePanel).position === 'fixed' && consoleBox.width && consoleBox.height
                    ? consolePanel.getBoundingClientRect().top
                    : window.innerHeight;
                  const build = document.querySelector('[data-testid="build-version"]');
                  const buildSafeTop = getComputedStyle(build).position === 'fixed'
                    ? build.getBoundingClientRect().top
                    : window.innerHeight;
                  const safeTop = Math.min(
                    window.innerHeight,
                    consoleSafeTop,
                    buildSafeTop
                  );
                  const deviceParts = [encoderRail, keyboard, bottomRail].filter((box) => box.width && box.height);
                  const device = {
                    left: Math.min(...deviceParts.map((box) => box.left)),
                    right: Math.max(...deviceParts.map((box) => box.right)),
                    top: Math.min(...deviceParts.map((box) => box.top)),
                    bottom: Math.max(...deviceParts.map((box) => box.bottom))
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
                if metrics["side"]["width"]:
                    self.assertLessEqual(metrics["device"]["right"], metrics["side"]["left"] - 8, metrics)
                self.assertLessEqual(metrics["device"]["bottom"], metrics["safeTop"] - 4, metrics)
                if metrics["bottomRail"]["width"] and metrics["encoderRail"]["width"]:
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
        self.open_hardware_tools()
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
        self.assertEqual(after_count, before_count)
        sent_after = self.page.evaluate("(before) => window.__mockExquisOutput.sent.slice(before)", before_count)
        self.assertNotIn([240, 0, 33, 126, 127, 6, 2, 247], sent_after)
        self.assertNotIn([240, 0, 33, 126, 127, 7, 1, 247], sent_after)
        self.assertEqual(sent_after, [])

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
        self.open_hardware_tools()
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.assertEqual(self.page.evaluate("() => window.__requests.map(r => !!r.sysex)"), [True, False])
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"exquis-sync-status\"]').textContent.includes('SysEx permission unavailable')")
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
        self.assertIn("Exquis Mock", self.page.locator('[data-testid="midi-input-select"]').text_content())
        self.assertIn("Exquis Mock", self.page.locator('[data-testid="midi-devices"]').text_content())
        target_midi = self.page.locator(".key.current").get_attribute("data-midi")
        self.page.evaluate("""
        (midi) => {
          window.__mockMidiInput.onmidimessage({ data: [0x90, Number(midi), 100] });
        }
        """, target_midi)
        self.assertIn("Correct", self.page.locator('[data-testid="coach-feedback"]').inner_text())
        self.assertIn("note-on", self.page.locator('[data-testid="midi-activity"]').text_content())
        self.assertIn("1 correct", self.page.locator('[data-testid="drill-score"]').inner_text())
        self.assertEqual(self.page.locator('[data-testid="calibration-stats"]').text_content(), "1 verified / 0 mismatched")

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
        self.assertIn("note-on", self.page.locator('[data-testid="midi-activity"]').text_content())

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

    def test_test_tone_creates_output_graph(self):
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
        self.page.locator('[data-testid="test-audio"]').click()
        events = self.page.evaluate("() => window.__audioEvents")
        starts = [event for event in events if event[0] == "start"]
        stops = [event for event in events if event[0] == "stop"]
        destination_connections = [event for event in events if event[0] == "connect" and event[2] == "destination"]
        self.assertGreaterEqual(len(starts), 1)
        self.assertGreaterEqual(len(stops), 1)
        self.assertGreaterEqual(len(destination_connections), 1)
        self.assertIn("Audio: playing C4.", self.page.locator('[data-testid="audio-status"]').inner_text())
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
            self.assertTrue(
                max(float(row["audioPeak"]), float(row["audioSpectrumPeak"])) >= 0.015 or float(row["audioRms"]) > 0.003,
                row,
            )
            self.assertLessEqual(float(row["audioClipRatio"]), 0.03, row)
            self.assertGreaterEqual(int(row["audioSignature"]["polyAftertouchEvents"]), 12, row)
            self.assertEqual(int(row["audioSignature"]["channelPressureEvents"]), 0, row)

    def test_regression_preset_sweep_runs_mature_engine_category_200_note_voice_stress_audio(self):
        def run_engine(engine):
            output_dir = ROOT / f"tmp_preset_sweep_unittest_voice_stress_{engine.lower()}"
            result = subprocess.run(
                [
                    "python",
                    "tools/preset_sweep.py",
                    "--no-build",
                    "--mature-engines-only",
                    "--one-per-category",
                    "--engine",
                    engine,
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
            payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
            return engine, result, payload

        shards = [run_engine(engine) for engine in ["Subtractive", "FM", "Physical"]]
        for engine, result, payload in shards:
            self.assertEqual(result.returncode, 0, f"{engine}\n{result.stdout}{result.stderr}\n{json.dumps(payload, indent=2)}")
        results = [row for _, _, payload in shards for row in payload["results"]]
        engines = {row["engine"].lower() for row in results}
        self.assertEqual(engines, {"fm", "physical", "subtractive"}, payload)
        self.assertGreaterEqual(len(results), 6, shards)
        for row in results:
            signature = row["audioSignature"]
            self.assertEqual(row["trigger"], "voice-stress-midi", row)
            self.assertTrue(row["audioSignatureAvailable"], row)
            self.assertEqual(int(signature["noteOns"]), 200, row)
            self.assertEqual(int(signature["noteOffs"]), 200, row)
            self.assertGreaterEqual(int(signature["observedMaxHeld"]), 6, row)
            physical = signature.get("physicalSettings") or {}
            release_strum_plucked = signature.get("instrumentType") == "physical" and physical.get("model") == "pluck"
            if release_strum_plucked:
                self.assertGreater(int(signature["ssliPluckedStartCount"]), 0, row)
            else:
                self.assertGreaterEqual(int(signature["observedMaxLocalVoices"]), 6, row)
            self.assertEqual(int(signature["voiceLossCount"]), 0, row)
            self.assertGreaterEqual(int(signature["polyAftertouchSent"]), 200, row)
            self.assertEqual(int(signature["channelPressureSent"]), 0, row)
            self.assertTrue(
                max(float(row["audioPeak"]), float(row["audioSpectrumPeak"])) >= 0.015 or float(row["audioRms"]) > 0.003,
                row,
            )
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
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x97, 48, 96] })")
        for pressure in [101, 104, 120, 0]:
            self.page.evaluate("(pressure) => window.__mockExquisInput.onmidimessage({ data: [0xD7, pressure] })", pressure)
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x87, 48, 0] })")
        self.page.wait_for_function("() => window.__ssliCalls.some(call => call[0] === 'physical.noteOn')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        pressure_updates = [call for call in calls if call[0] == "physical.updateNotePressure"]
        note_ons = [call for call in calls if call[0] == "physical.noteOn"]
        self.assertEqual(pressure_updates, [], calls)
        self.assertEqual([call[1] for call in note_ons], [48], calls)
        self.assertGreaterEqual(note_ons[0][2], 54, calls)
        self.assertIn("physical.noteOn", [call[0] for call in calls])

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
        self.assertIn("articulation queued B2 mode=release-strum", metrics["diagnosticLog"])
        self.assertIn("articulation queued C3 mode=release-strum", metrics["diagnosticLog"])
        self.assertIn("articulation flush mode=release-strum family=plucked notes=B2,C3", metrics["diagnosticLog"])
        self.assertNotIn("semitoneJamGuard", metrics["diagnosticLog"])
        self.assertIn("SSLI plucked one-shot B2 velocity=50", metrics["diagnosticLog"])
        self.assertIn("SSLI plucked one-shot C3 velocity=54", metrics["diagnosticLog"])
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
        self.assertIn("articulation flush mode=release-strum", metrics["diagnosticLog"])
        self.assertIn("SSLI plucked one-shot", metrics["diagnosticLog"])
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
          await new Promise(resolve => setTimeout(resolve, 220));
        }
        """)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("articulation flush mode=release-strum family=plucked notes=E3", log)
        self.assertIn("articulation flush mode=release-strum family=plucked notes=B3,G3", log)
        self.assertIn("SSLI plucked one-shot B3", log)
        self.assertIn("SSLI plucked one-shot G3", log)
        self.assertIn("SSLI plucked one-shot E3", log)
        self.assertNotIn("articulation skipped released E3", log)

    def test_regression_real_plucked_release_strum_press_has_no_audio_transient(self):
        from tools.preset_signature_check import start_server

        server, url = start_server()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.page.goto(url)
        self.page.wait_for_selector('[data-testid="sound-engine-select"]')
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__releasePressMidiInput = { id: 'release-press-exquis', name: 'Release Press Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__releasePressMidiInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__releasePressMidiInput && window.__releasePressMidiInput.onmidimessage")
        self.page.select_option('[data-testid="sound-engine-select"]', label="Physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        metrics = self.page.evaluate("""
        async () => {
          const input = window.__releasePressMidiInput;
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow;
          const SL = host && host.SynthLab;
          const ctx = SL && SL.audio && SL.audio.getCtx ? SL.audio.getCtx() : null;
          const masterOutput = SL && SL.audio && SL.audio.getInstruments && SL.audio.getInstruments()[0] && SL.audio.getInstruments()[0].masterOutput;
          if (!ctx || !masterOutput) return { available: false, error: 'missing SSLI master output path' };
          window.__realPhysicalNoteOns = [];
          const originalPhysicalNoteOn = SL.physical.noteOn.bind(SL.physical);
          const originalPhysicalNoteOff = SL.physical.noteOff.bind(SL.physical);
          const originalPhysicalNoteOffVoice = SL.physical.noteOffVoice.bind(SL.physical);
          const originalPhysicalSilenceVoice = SL.physical.silenceVoice.bind(SL.physical);
          SL.physical.noteOn = (midi, velocity, inst, options) => {
            window.__realPhysicalNoteOns.push({ midi, velocity, inst, options: options || null });
            return originalPhysicalNoteOn(midi, velocity, inst, options);
          };
          window.__realPhysicalNoteOffs = [];
          SL.physical.noteOff = (midi, inst) => {
            window.__realPhysicalNoteOffs.push({ midi, inst });
            return originalPhysicalNoteOff(midi, inst);
          };
          window.__realPhysicalNoteOffVoices = [];
          SL.physical.noteOffVoice = (voiceId, inst) => {
            window.__realPhysicalNoteOffVoices.push({ voiceId, inst });
            return originalPhysicalNoteOffVoice(voiceId, inst);
          };
          window.__realPhysicalSilenceVoices = [];
          SL.physical.silenceVoice = (voiceId, inst) => {
            window.__realPhysicalSilenceVoices.push({ voiceId, inst });
            return originalPhysicalSilenceVoice(voiceId, inst);
          };
          if (ctx.state === 'suspended') await ctx.resume();
          const analyser = ctx.createAnalyser();
          analyser.fftSize = 2048;
          masterOutput.connect(analyser);
          const wave = new Uint8Array(analyser.fftSize);
          const sampleWindow = async (ms) => {
            let peak = 0;
            let rmsSum = 0;
            let count = 0;
            const start = Date.now();
            while (Date.now() - start < ms) {
              analyser.getByteTimeDomainData(wave);
              for (let i = 0; i < wave.length; i += 1) {
                const n = (wave[i] - 128) / 128;
                peak = Math.max(peak, Math.abs(n));
                rmsSum += n * n;
                count += 1;
              }
              await new Promise(resolve => setTimeout(resolve, 8));
            }
            return { peak: Number(peak.toFixed(5)), rms: Number(Math.sqrt(rmsSum / Math.max(1, count)).toFixed(5)) };
          };
          const send = (data) => input.onmidimessage({ data });
          send([0x92, 53, 90]);
          send([0xD2, 114]);
          send([0xD2, 0]);
          send([0x82, 53, 0]);
          await new Promise(resolve => setTimeout(resolve, 40));
          const tailBeforePress = await sampleWindow(12);
          send([0x93, 50, 113]);
          send([0xD3, 118]);
          const pressBuffer = await sampleWindow(20);
          await new Promise(resolve => setTimeout(resolve, 35));
          const pressSettled = await sampleWindow(80);
          send([0xD3, 0]);
          send([0x83, 50, 0]);
          await new Promise(resolve => setTimeout(resolve, 180));
          const releasePluck = await sampleWindow(180);
          try { masterOutput.disconnect(analyser); } catch (err) {}
          return {
            available: true,
            tailBeforePress,
            pressBuffer,
            pressSettled,
            releasePluck,
            physicalNoteOns: window.__realPhysicalNoteOns,
            physicalNoteOffs: window.__realPhysicalNoteOffs,
            physicalNoteOffVoices: window.__realPhysicalNoteOffVoices,
            physicalSilenceVoices: window.__realPhysicalSilenceVoices,
            diagnosticLog: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
        }
        """)
        self.assertTrue(metrics.get("available"), metrics)
        self.assertNotIn("cancelled release pluck on transition F3 -> D3", metrics["diagnosticLog"])
        self.assertNotIn("absorbed release-strum tail on new contact F3 -> D3", metrics["diagnosticLog"])
        self.assertIn("articulation queued D3 mode=release-strum", metrics["diagnosticLog"])
        self.assertEqual([call["midi"] for call in metrics["physicalNoteOns"]], [53, 50], metrics)
        self.assertEqual([call["options"]["maxDurationMs"] for call in metrics["physicalNoteOns"]], [320, 320], metrics)
        self.assertTrue(all(call["options"].get("voiceId", "").startswith("exquis-pluck-") for call in metrics["physicalNoteOns"]), metrics)
        self.assertEqual(metrics["physicalNoteOffs"], [], metrics)
        self.assertEqual(metrics["physicalNoteOffVoices"], [], metrics)
        self.assertEqual(metrics["physicalSilenceVoices"], [], metrics)
        self.assertIn("note-on D3", metrics["diagnosticLog"])
        self.assertIn("note-off D3", metrics["diagnosticLog"])
        self.assertGreater(metrics["releasePluck"]["peak"], 0.04, metrics)
        self.assertGreater(metrics["releasePluck"]["rms"], 0.008, metrics)

    def test_regression_real_plucked_same_pitch_fast_repress_finger_mutes_old_tail_without_new_pluck(self):
        from tools.preset_signature_check import start_server

        server, url = start_server()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.page.goto(url)
        self.page.wait_for_selector('[data-testid="sound-engine-select"]')
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__samePitchRepressInput = { id: 'same-pitch-repress-exquis', name: 'Same Pitch Repress Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__samePitchRepressInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__samePitchRepressInput && window.__samePitchRepressInput.onmidimessage")
        self.page.select_option('[data-testid="sound-engine-select"]', label="Physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        metrics = self.page.evaluate("""
        async () => {
          const input = window.__samePitchRepressInput;
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow;
          const SL = host && host.SynthLab;
          const ctx = SL && SL.audio && SL.audio.getCtx ? SL.audio.getCtx() : null;
          const masterOutput = SL && SL.audio && SL.audio.getInstruments && SL.audio.getInstruments()[0] && SL.audio.getInstruments()[0].masterOutput;
          if (!ctx || !masterOutput) return { available: false, error: 'missing SSLI master output path' };
          window.__realPhysicalNoteOns = [];
          const originalPhysicalNoteOn = SL.physical.noteOn.bind(SL.physical);
          const originalPhysicalNoteOff = SL.physical.noteOff.bind(SL.physical);
          const originalPhysicalNoteOffVoice = SL.physical.noteOffVoice.bind(SL.physical);
          const originalPhysicalSilenceVoice = SL.physical.silenceVoice.bind(SL.physical);
          SL.physical.noteOn = (midi, velocity, inst, options) => {
            window.__realPhysicalNoteOns.push({ midi, velocity, inst, options: options || null });
            return originalPhysicalNoteOn(midi, velocity, inst, options);
          };
          window.__realPhysicalNoteOffs = [];
          SL.physical.noteOff = (midi, inst) => {
            window.__realPhysicalNoteOffs.push({ midi, inst });
            return originalPhysicalNoteOff(midi, inst);
          };
          window.__realPhysicalNoteOffVoices = [];
          SL.physical.noteOffVoice = (voiceId, inst) => {
            window.__realPhysicalNoteOffVoices.push({ voiceId, inst });
            return originalPhysicalNoteOffVoice(voiceId, inst);
          };
          window.__realPhysicalSilenceVoices = [];
          SL.physical.silenceVoice = (voiceId, inst) => {
            window.__realPhysicalSilenceVoices.push({ voiceId, inst });
            return originalPhysicalSilenceVoice(voiceId, inst);
          };
          if (ctx.state === 'suspended') await ctx.resume();
          const analyser = ctx.createAnalyser();
          analyser.fftSize = 2048;
          masterOutput.connect(analyser);
          const wave = new Uint8Array(analyser.fftSize);
          const sampleWindow = async (ms) => {
            let peak = 0;
            let rmsSum = 0;
            let count = 0;
            const start = Date.now();
            while (Date.now() - start < ms) {
              analyser.getByteTimeDomainData(wave);
              for (let i = 0; i < wave.length; i += 1) {
                const n = (wave[i] - 128) / 128;
                peak = Math.max(peak, Math.abs(n));
                rmsSum += n * n;
                count += 1;
              }
              await new Promise(resolve => setTimeout(resolve, 8));
            }
            return { peak: Number(peak.toFixed(5)), rms: Number(Math.sqrt(rmsSum / Math.max(1, count)).toFixed(5)) };
          };
          const send = (data) => input.onmidimessage({ data });
          send([0x97, 53, 65]);
          send([0xD7, 96]);
          send([0xD7, 0]);
          send([0x87, 53, 0]);
          await new Promise(resolve => setTimeout(resolve, 28));
          const tailBeforeRepress = await sampleWindow(12);
          send([0x92, 53, 116]);
          send([0xD2, 127]);
          const repressOnly = await sampleWindow(80);
          send([0x92, 49, 1]);
          send([0x82, 49, 0]);
          await new Promise(resolve => setTimeout(resolve, 60));
          const contactNoiseWindow = await sampleWindow(60);
          send([0xD2, 0]);
          send([0x82, 53, 0]);
          await new Promise(resolve => setTimeout(resolve, 180));
          const releasePluck = await sampleWindow(180);
          try { masterOutput.disconnect(analyser); } catch (err) {}
          return {
            available: true,
            tailBeforeRepress,
            repressOnly,
            contactNoiseWindow,
            releasePluck,
            physicalNoteOns: window.__realPhysicalNoteOns,
            physicalNoteOffs: window.__realPhysicalNoteOffs,
            physicalNoteOffVoices: window.__realPhysicalNoteOffVoices,
            physicalSilenceVoices: window.__realPhysicalSilenceVoices,
            diagnosticLog: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
        }
        """)
        self.assertTrue(metrics.get("available"), metrics)
        self.assertNotIn("cancelled release pluck on transition F3 -> F3", metrics["diagnosticLog"])
        self.assertIn("release-strum note-up candidate F3", metrics["diagnosticLog"])
        self.assertIn("release-strum immediate commit F3", metrics["diagnosticLog"])
        self.assertIn("release-strum commit start F3", metrics["diagnosticLog"])
        self.assertIn("silenced same-key release pluck on recontact F3 voice=exquis-pluck-1", metrics["diagnosticLog"])
        self.assertIn("note-on ignored release-strum contact noise C#3", metrics["diagnosticLog"])
        self.assertEqual([call["midi"] for call in metrics["physicalNoteOns"]], [53, 53], metrics)
        self.assertEqual([call["options"]["maxDurationMs"] for call in metrics["physicalNoteOns"]], [320, 320], metrics)
        self.assertEqual([call["options"]["voiceId"] for call in metrics["physicalNoteOns"]], ["exquis-pluck-1", "exquis-pluck-2"], metrics)
        self.assertEqual(metrics["physicalNoteOffs"], [], metrics)
        self.assertEqual(metrics["physicalNoteOffVoices"], [], metrics)
        self.assertEqual([call["voiceId"] for call in metrics["physicalSilenceVoices"]], ["exquis-pluck-1"], metrics)
        self.assertLess(metrics["contactNoiseWindow"]["peak"], 0.025, metrics)
        self.assertGreater(metrics["releasePluck"]["peak"], 0.05, metrics)

    def test_regression_real_plucked_immediate_repress_does_not_emit_prior_release(self):
        from tools.preset_signature_check import start_server

        server, url = start_server()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.page.goto(url)
        self.page.wait_for_selector('[data-testid="sound-engine-select"]')
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__committedTailRepressInput = { id: 'committed-tail-repress-exquis', name: 'Committed Tail Repress Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__committedTailRepressInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__committedTailRepressInput && window.__committedTailRepressInput.onmidimessage")
        self.page.select_option('[data-testid="sound-engine-select"]', label="Physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        metrics = self.page.evaluate("""
        async () => {
          const input = window.__committedTailRepressInput;
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow;
          const SL = host && host.SynthLab;
          const ctx = SL && SL.audio && SL.audio.getCtx ? SL.audio.getCtx() : null;
          const masterOutput = SL && SL.audio && SL.audio.getInstruments && SL.audio.getInstruments()[0] && SL.audio.getInstruments()[0].masterOutput;
          if (!SL || !SL.physical || !ctx || !masterOutput) return { available: false, error: 'missing physical runtime' };
          window.__realPhysicalNoteOns = [];
          window.__realPhysicalNoteOffs = [];
          window.__realPhysicalNoteOffVoices = [];
          window.__realPhysicalSilenceVoices = [];
          const originalPhysicalNoteOn = SL.physical.noteOn.bind(SL.physical);
          const originalPhysicalNoteOff = SL.physical.noteOff.bind(SL.physical);
          const originalPhysicalNoteOffVoice = SL.physical.noteOffVoice.bind(SL.physical);
          const originalPhysicalSilenceVoice = SL.physical.silenceVoice.bind(SL.physical);
          SL.physical.noteOn = (midi, velocity, inst, options) => {
            window.__realPhysicalNoteOns.push({ midi, velocity, inst, options: options || null, at: performance.now() });
            return originalPhysicalNoteOn(midi, velocity, inst, options);
          };
          SL.physical.noteOff = (midi, inst) => {
            window.__realPhysicalNoteOffs.push({ midi, inst, at: performance.now() });
            return originalPhysicalNoteOff(midi, inst);
          };
          SL.physical.noteOffVoice = (voiceId, inst) => {
            window.__realPhysicalNoteOffVoices.push({ voiceId, inst, at: performance.now() });
            return originalPhysicalNoteOffVoice(voiceId, inst);
          };
          SL.physical.silenceVoice = (voiceId, inst) => {
            window.__realPhysicalSilenceVoices.push({ voiceId, inst, at: performance.now() });
            return originalPhysicalSilenceVoice(voiceId, inst);
          };
          if (ctx.state === 'suspended') await ctx.resume();
          const analyser = ctx.createAnalyser();
          analyser.fftSize = 2048;
          masterOutput.connect(analyser);
          const wave = new Uint8Array(analyser.fftSize);
          const sampleWindow = async (ms) => {
            let peak = 0;
            let rmsSum = 0;
            let count = 0;
            const start = performance.now();
            while (performance.now() - start < ms) {
              analyser.getByteTimeDomainData(wave);
              for (let i = 0; i < wave.length; i += 1) {
                const n = (wave[i] - 128) / 128;
                peak = Math.max(peak, Math.abs(n));
                rmsSum += n * n;
                count += 1;
              }
              await new Promise(resolve => setTimeout(resolve, 8));
            }
            return { peak: Number(peak.toFixed(5)), rms: Number(Math.sqrt(rmsSum / Math.max(1, count)).toFixed(5)) };
          };
          const send = (data) => input.onmidimessage({ data });
          send([0x97, 53, 77]);
          send([0xD7, 105]);
          send([0xD7, 0]);
          send([0x87, 53, 0]);
          await new Promise(resolve => setTimeout(resolve, 40));
          const firstReleaseStarted = window.__realPhysicalNoteOns.length;
          const quietBeforePress = await sampleWindow(18);
          window.__pressAt = performance.now();
          send([0x91, 53, 86]);
          send([0xD1, 112]);
          await new Promise(resolve => setTimeout(resolve, 100));
          const postRecontact = await sampleWindow(70);
          await new Promise(resolve => setTimeout(resolve, 80));
          const duringPress = {
            noteOns: window.__realPhysicalNoteOns.slice(),
            noteOffs: window.__realPhysicalNoteOffs.slice(),
            noteOffVoices: window.__realPhysicalNoteOffVoices.slice(),
            silenceVoices: window.__realPhysicalSilenceVoices.slice(),
            log: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
          send([0xD1, 0]);
          send([0x81, 53, 0]);
          await new Promise(resolve => setTimeout(resolve, 180));
          try { masterOutput.disconnect(analyser); } catch (err) {}
          return {
            available: true,
            firstReleaseStarted,
            quietBeforePress,
            postRecontact,
            duringPress,
            finalNoteOns: window.__realPhysicalNoteOns,
            diagnosticLog: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
        }
        """)
        self.assertTrue(metrics.get("available"), metrics)
        self.assertEqual(metrics["firstReleaseStarted"], 1, metrics)
        self.assertEqual([call["midi"] for call in metrics["duringPress"]["noteOns"]], [53], metrics)
        self.assertEqual(metrics["duringPress"]["noteOffs"], [], metrics)
        self.assertEqual(metrics["duringPress"]["noteOffVoices"], [], metrics)
        self.assertEqual([call["voiceId"] for call in metrics["duringPress"]["silenceVoices"]], ["exquis-pluck-1"], metrics)
        self.assertNotIn("absorbed release-strum tail on new contact", metrics["duringPress"]["log"])
        self.assertNotIn("finger-muted ringing release pluck on new contact", metrics["duringPress"]["log"])
        self.assertNotIn("cancelled release pluck on transition F3 -> F3", metrics["duringPress"]["log"])
        self.assertIn("silenced same-key release pluck on recontact F3 voice=exquis-pluck-1", metrics["duringPress"]["log"])
        self.assertLess(metrics["postRecontact"]["peak"], 0.025, metrics)
        self.assertLess(metrics["postRecontact"]["rms"], 0.006, metrics)
        self.assertEqual([call["midi"] for call in metrics["finalNoteOns"]], [53, 53], metrics)

    def test_regression_real_plucked_same_key_recontact_damps_committed_release_tail(self):
        from tools.preset_signature_check import start_server

        server, url = start_server()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.page.goto(url)
        self.page.wait_for_selector('[data-testid="sound-engine-select"]')
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__sameKeyCommittedInput = { id: 'same-key-committed-exquis', name: 'Same Key Committed Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__sameKeyCommittedInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__sameKeyCommittedInput && window.__sameKeyCommittedInput.onmidimessage")
        self.page.select_option('[data-testid="sound-engine-select"]', label="Physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        metrics = self.page.evaluate("""
        async () => {
          const input = window.__sameKeyCommittedInput;
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow;
          const SL = host && host.SynthLab;
          if (!SL || !SL.physical) return { available: false, error: 'missing physical runtime' };
          window.__realPhysicalNoteOns = [];
          window.__realPhysicalNoteOffVoices = [];
          window.__realPhysicalSilenceVoices = [];
          const originalPhysicalNoteOn = SL.physical.noteOn.bind(SL.physical);
          const originalPhysicalNoteOffVoice = SL.physical.noteOffVoice.bind(SL.physical);
          const originalPhysicalSilenceVoice = SL.physical.silenceVoice.bind(SL.physical);
          SL.physical.noteOn = (midi, velocity, inst, options) => {
            window.__realPhysicalNoteOns.push({ midi, velocity, inst, options: options || null, at: performance.now() });
            return originalPhysicalNoteOn(midi, velocity, inst, options);
          };
          SL.physical.noteOffVoice = (voiceId, inst) => {
            window.__realPhysicalNoteOffVoices.push({ voiceId, inst, at: performance.now() });
            return originalPhysicalNoteOffVoice(voiceId, inst);
          };
          SL.physical.silenceVoice = (voiceId, inst) => {
            window.__realPhysicalSilenceVoices.push({ voiceId, inst, at: performance.now() });
            return originalPhysicalSilenceVoice(voiceId, inst);
          };
          const send = (data) => input.onmidimessage({ data });
          send([0x96, 53, 78]);
          send([0xD6, 106]);
          send([0xD6, 0]);
          send([0x86, 53, 0]);
          await new Promise(resolve => setTimeout(resolve, 230));
          const committedCount = window.__realPhysicalNoteOns.length;
          send([0x94, 53, 125]);
          send([0xD4, 127]);
          await new Promise(resolve => setTimeout(resolve, 160));
          const duringHold = {
            noteOns: window.__realPhysicalNoteOns.slice(),
            noteOffVoices: window.__realPhysicalNoteOffVoices.slice(),
            silenceVoices: window.__realPhysicalSilenceVoices.slice(),
            log: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
          send([0xD4, 0]);
          send([0x84, 53, 0]);
          await new Promise(resolve => setTimeout(resolve, 180));
          return {
            available: true,
            committedCount,
            duringHold,
            finalNoteOns: window.__realPhysicalNoteOns,
            diagnosticLog: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
        }
        """)
        self.assertTrue(metrics.get("available"), metrics)
        self.assertEqual(metrics["committedCount"], 1, metrics)
        self.assertEqual([call["midi"] for call in metrics["duringHold"]["noteOns"]], [53], metrics)
        self.assertEqual(metrics["duringHold"]["noteOffVoices"], [], metrics)
        self.assertEqual([call["voiceId"] for call in metrics["duringHold"].get("silenceVoices", [])], ["exquis-pluck-1"], metrics)
        self.assertIn("silenced same-key release pluck on recontact F3 voice=exquis-pluck-1", metrics["duringHold"]["log"])
        self.assertNotIn("after-one-shot-expire F3 held=1 local=0", metrics["diagnosticLog"])
        self.assertEqual([call["midi"] for call in metrics["finalNoteOns"]], [53, 53], metrics)

    def test_regression_real_plucked_release_pluck_starts_on_note_up_without_scheduled_attack(self):
        from tools.preset_signature_check import start_server

        server, url = start_server()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        self.page.goto(url)
        self.page.wait_for_selector('[data-testid="sound-engine-select"]')
        self.open_audio_drawer()
        self.page.evaluate("""
        () => {
          window.__sameKeyScheduledInput = { id: 'same-key-scheduled-exquis', name: 'Same Key Scheduled Exquis', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__sameKeyScheduledInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__sameKeyScheduledInput && window.__sameKeyScheduledInput.onmidimessage")
        self.page.select_option('[data-testid="sound-engine-select"]', label="Physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        metrics = self.page.evaluate("""
        async () => {
          const input = window.__sameKeyScheduledInput;
          const frame = document.getElementById('ssliEngineFrame');
          const host = frame && frame.contentWindow;
          const SL = host && host.SynthLab;
          if (!SL || !SL.physical) return { available: false, error: 'missing physical runtime' };
          window.__realPhysicalNoteOns = [];
          const originalPhysicalNoteOn = SL.physical.noteOn.bind(SL.physical);
          SL.physical.noteOn = (midi, velocity, inst, options) => {
            window.__realPhysicalNoteOns.push({ midi, velocity, inst, options: options || null, at: performance.now() });
            return originalPhysicalNoteOn(midi, velocity, inst, options);
          };
          const send = (data) => input.onmidimessage({ data });
          send([0x96, 53, 64]);
          send([0xD6, 112]);
          send([0xD6, 0]);
          send([0x86, 53, 0]);
          await new Promise(resolve => setTimeout(resolve, 20));
          const beforeRecontactOns = window.__realPhysicalNoteOns.slice();
          send([0x94, 53, 81]);
          send([0xD4, 90]);
          await new Promise(resolve => setTimeout(resolve, 120));
          const duringHold = {
            noteOns: window.__realPhysicalNoteOns.slice(),
            log: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
          send([0xD4, 0]);
          send([0x84, 53, 0]);
          await new Promise(resolve => setTimeout(resolve, 220));
          return {
            available: true,
            beforeRecontactOns,
            duringHold,
            finalNoteOns: window.__realPhysicalNoteOns,
            diagnosticLog: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
        }
        """)
        self.assertTrue(metrics.get("available"), metrics)
        self.assertEqual([call["midi"] for call in metrics["beforeRecontactOns"]], [53], metrics)
        self.assertEqual([call["midi"] for call in metrics["duringHold"]["noteOns"]], [53], metrics)
        self.assertIn("articulation flush mode=release-strum family=plucked notes=F3", metrics["duringHold"]["log"])
        self.assertNotIn("cancelled scheduled release pluck on recontact F3 -> F3", metrics["duringHold"]["log"])
        self.assertIn("silenced same-key release pluck on recontact F3 voice=exquis-pluck-1", metrics["duringHold"]["log"])
        self.assertEqual([call["midi"] for call in metrics["finalNoteOns"]], [53, 53], metrics)

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
            name: instrumentType === 'physical' && physicalModel === 'strike' ? 'Marimba' : (instrumentType === 'physical' ? 'Nylon Guitar' : 'Soft EP'),
            category: instrumentType === 'physical' && physicalModel === 'strike' ? 'Struck' : (instrumentType === 'physical' ? 'Plucked' : 'Keys'),
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
              noteOn(midi, velocity, inst, options) { window.__ssliCalls.push(['physical.noteOn', midi, velocity, inst, performance.now(), options || null]); },
              noteOff(midi, inst) { window.__ssliCalls.push(['physical.noteOff', midi, inst, performance.now()]); },
              noteOffVoice(voiceId, inst) { window.__ssliCalls.push(['physical.noteOffVoice', voiceId, inst, performance.now()]); },
              silenceVoice(voiceId, inst) { window.__ssliCalls.push(['physical.silenceVoice', voiceId, inst, performance.now()]); },
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
          window.__mockExquisInput.onmidimessage({ data: [0x81, 47, 0] });
          window.__mockExquisInput.onmidimessage({ data: [0x82, 48, 0] });
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
        self.assertIn("articulation queued B2 mode=release-strum", metrics["log"])
        self.assertEqual(metrics["pressure"], [], metrics)

    def test_regression_plucked_presets_trigger_on_note_up_not_note_down(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 24] });
        }
        """)
        self.page.wait_for_timeout(80)
        self.assertEqual(self.page.evaluate("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn')"), [])
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0xA1, 48, 104] });
          window.__mockExquisInput.onmidimessage({ data: [0x81, 48, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.some(call => call[0] === 'physical.noteOn')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        note_ons = [call for call in calls if call[0] == "physical.noteOn"]
        self.assertEqual([call[1] for call in note_ons], [48], calls)
        self.assertGreaterEqual(note_ons[0][2], 90, calls)
        self.assertEqual(note_ons[0][5]["maxDurationMs"], 320, calls)
        self.assertEqual(note_ons[0][5]["voiceId"], "exquis-pluck-1", calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("articulation queued C3 mode=release-strum", log)

    def test_regression_plucked_duplicate_channel_press_does_not_fire_old_pending_release(self):
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
          window.__pluckTiming = {};
          input.onmidimessage({ data: [0x91, 48, 86] });
          input.onmidimessage({ data: [0x81, 48, 0] });
          setTimeout(() => {
            window.__pluckTiming.secondPressAt = performance.now();
            input.onmidimessage({ data: [0x92, 48, 93] });
          }, 45);
        }
        """)
        self.page.wait_for_timeout(190)
        during_new_press = self.page.evaluate("""
        () => ({
          starts: window.__ssliCalls.filter(call => call[0] === 'physical.noteOn'),
          calls: window.__ssliCalls,
          debug: window.__exquisDebugSnapshot(),
          timing: window.__pluckTiming,
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual([call[1] for call in during_new_press["starts"]], [], during_new_press)
        self.assertEqual(during_new_press["debug"]["heldNotes"], 1, during_new_press)
        self.assertNotIn("released duplicate MIDI voice C3", during_new_press["log"])
        self.assertEqual([call[1] for call in during_new_press["calls"] if call[0] == "physical.noteOff"], [], during_new_press)
        self.assertEqual([call[1] for call in during_new_press["calls"] if call[0] == "physical.noteOffVoice"], [], during_new_press)
        self.assertEqual([call[1] for call in during_new_press["calls"] if call[0] == "physical.silenceVoice"], [], during_new_press)
        self.assertEqual([call for call in during_new_press["calls"] if call[0] == "setExpression"], [], during_new_press)
        self.assertEqual([call for call in during_new_press["calls"] if call[0] == "physical.updateNotePressure"], [], during_new_press)
        self.assertIn("absorbed release-strum precontact C3 on recontact", during_new_press["log"])
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x82, 48, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length === 1")
        calls = self.page.evaluate("() => window.__ssliCalls")
        note_ons = [call for call in calls if call[0] == "physical.noteOn"]
        self.assertEqual([call[1] for call in note_ons], [48], calls)

    def test_regression_plucked_short_release_fires_before_next_different_press(self):
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
          window.__pluckTiming = {};
          window.__ssliCalls.length = 0;
          input.onmidimessage({ data: [0x91, 48, 86] });
          input.onmidimessage({ data: [0x81, 48, 0] });
          window.__pluckTiming.firstReleaseAt = performance.now();
          setTimeout(() => {
            window.__pluckTiming.secondPressAt = performance.now();
            input.onmidimessage({ data: [0x92, 50, 93] });
          }, 70);
        }
        """)
        self.page.wait_for_function("() => window.__pluckTiming && window.__pluckTiming.secondPressAt")
        self.page.wait_for_timeout(220)
        metrics = self.page.evaluate("""
        () => {
          const c3 = window.__ssliCalls.find(call => call[0] === 'physical.noteOn' && call[1] === 48);
          return {
            c3,
            timing: window.__pluckTiming,
            calls: window.__ssliCalls,
            log: document.querySelector('[data-testid="diagnostic-log"]').textContent
          };
        }
        """)
        self.assertIsNotNone(metrics["c3"], metrics)
        self.assertNotIn("cancelled release pluck on transition C3 -> D3", metrics["log"])
        self.assertNotIn("note-off delayed short hold C3", metrics["log"])
        self.assertEqual([call for call in metrics["calls"] if call[0] == "physical.noteOn" and call[1] == 50], [], metrics)

    def test_regression_plucked_ignores_velocity_one_contact_noise_while_held(self):
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
          input.onmidimessage({ data: [0x94, 53, 124] });
          input.onmidimessage({ data: [0xD4, 127] });
          input.onmidimessage({ data: [0x9C, 56, 4] });
          input.onmidimessage({ data: [0xDC, 19] });
          input.onmidimessage({ data: [0xDC, 0] });
          input.onmidimessage({ data: [0x8C, 56, 0] });
        }
        """)
        self.page.wait_for_timeout(90)
        metrics = self.page.evaluate("""
        () => ({
          calls: window.__ssliCalls,
          debug: window.__exquisDebugSnapshot(),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual([call for call in metrics["calls"] if call[0] == "physical.noteOn"], [], metrics)
        self.assertEqual(metrics["debug"]["heldNotes"], 1, metrics)
        self.assertIn("ignored release-strum weak contact G#3 peakPressure=19 min=48", metrics["log"])
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x84, 53, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length === 1")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual([call[1] for call in calls if call[0] == "physical.noteOn"], [53], calls)

    def test_regression_plucked_exquis_low_velocity_pressure_spike_contact_noise_does_not_pluck(self):
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
          input.onmidimessage({ data: [0x91, 60, 4] });
          input.onmidimessage({ data: [0xD1, 12] });
          input.onmidimessage({ data: [0xD1, 36] });
          input.onmidimessage({ data: [0xD1, 0] });
          input.onmidimessage({ data: [0x81, 60, 0] });
        }
        """)
        self.page.wait_for_timeout(90)
        metrics = self.page.evaluate("""
        () => ({
          calls: window.__ssliCalls,
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual([call for call in metrics["calls"] if call[0] == "physical.noteOn"], [], metrics)
        self.assertIn("ignored release-strum weak contact C4 peakPressure=36 min=48", metrics["log"])
        self.assertNotIn("SSLI plucked one-shot C4", metrics["log"])

    def test_regression_plucked_low_velocity_real_pressure_release_still_plucks(self):
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
          window.__ssliCalls.length = 0;
          input.onmidimessage({ data: [0x94, 53, 4] });
          input.onmidimessage({ data: [0xD4, 63] });
          input.onmidimessage({ data: [0xD4, 0] });
          input.onmidimessage({ data: [0x84, 53, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.some(call => call[0] === 'physical.noteOn' && call[1] === 53)")
        metrics = self.page.evaluate("""
        () => ({
          calls: window.__ssliCalls,
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        note_ons = [call for call in metrics["calls"] if call[0] == "physical.noteOn"]
        self.assertEqual([call[1] for call in note_ons], [53], metrics)
        self.assertNotIn("ignored release-strum weak contact F3", metrics["log"])

    def test_regression_plucked_exquis_ambiguous_release_absorbs_immediate_same_key_recontact(self):
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
          window.__ssliCalls.length = 0;
          input.onmidimessage({ data: [0x93, 53, 32] });
          input.onmidimessage({ data: [0xD3, 58] });
          input.onmidimessage({ data: [0xD3, 81] });
          input.onmidimessage({ data: [0xD3, 0] });
          input.onmidimessage({ data: [0x83, 53, 0] });
          setTimeout(() => {
            input.onmidimessage({ data: [0x94, 53, 83] });
            input.onmidimessage({ data: [0xD4, 104] });
          }, 18);
        }
        """)
        self.page.wait_for_timeout(120)
        metrics = self.page.evaluate("""
        () => ({
          calls: window.__ssliCalls,
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent,
          debug: window.__exquisDebugSnapshot()
        })
        """)
        self.assertEqual([call for call in metrics["calls"] if call[0] == "physical.noteOn"], [], metrics)
        self.assertEqual(metrics["debug"]["heldNotes"], 1, metrics)
        self.assertIn("absorbed release-strum precontact F3 on recontact", metrics["log"])
        self.assertNotIn("SSLI plucked one-shot F3 velocity=96 pressure=81", metrics["log"])
        self.page.evaluate("""
        () => {
          const input = window.__mockExquisInput;
          input.onmidimessage({ data: [0xD4, 127] });
          input.onmidimessage({ data: [0xD4, 0] });
          input.onmidimessage({ data: [0x84, 53, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length === 1")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual([call[1] for call in calls if call[0] == "physical.noteOn"], [53], calls)

    def test_regression_plucked_exquis_repeated_ambiguous_same_key_contacts_absorb_until_final_release(self):
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
          window.__ssliCalls.length = 0;
          input.onmidimessage({ data: [0x97, 50, 50] });
          input.onmidimessage({ data: [0xD7, 79] });
          input.onmidimessage({ data: [0xD7, 82] });
          input.onmidimessage({ data: [0xD7, 0] });
          input.onmidimessage({ data: [0x87, 50, 0] });
          setTimeout(() => {
            input.onmidimessage({ data: [0x96, 50, 58] });
            input.onmidimessage({ data: [0xD6, 70] });
            input.onmidimessage({ data: [0xD6, 94] });
            input.onmidimessage({ data: [0xD6, 0] });
            input.onmidimessage({ data: [0x86, 50, 0] });
          }, 80);
          setTimeout(() => {
            input.onmidimessage({ data: [0x91, 50, 91] });
            input.onmidimessage({ data: [0xD1, 107] });
            input.onmidimessage({ data: [0xD1, 127] });
          }, 150);
        }
        """)
        self.page.wait_for_timeout(260)
        metrics = self.page.evaluate("""
        () => ({
          calls: window.__ssliCalls,
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent,
          debug: window.__exquisDebugSnapshot()
        })
        """)
        self.assertEqual([call for call in metrics["calls"] if call[0] == "physical.noteOn"], [], metrics)
        self.assertEqual(metrics["debug"]["heldNotes"], 1, metrics)
        self.assertGreaterEqual(metrics["log"].count("absorbed release-strum precontact D3 on recontact"), 2, metrics)
        self.assertNotIn("SSLI plucked one-shot D3 velocity=96 pressure=82", metrics["log"])
        self.assertNotIn("SSLI plucked one-shot D3 velocity=96 pressure=94", metrics["log"])
        self.page.evaluate("""
        () => {
          const input = window.__mockExquisInput;
          input.onmidimessage({ data: [0xD1, 0] });
          input.onmidimessage({ data: [0x81, 50, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length === 1")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual([call[1] for call in calls if call[0] == "physical.noteOn"], [50], calls)

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
          window.__mockExquisInput.onmidimessage({ data: [0x8A, 53, 0] });
          window.__mockExquisInput.onmidimessage({ data: [0x8D, 47, 0] });
          window.__mockExquisInput.onmidimessage({ data: [0x86, 50, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 3")
        calls = self.page.evaluate("() => window.__ssliCalls")
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertEqual([call[0] for call in calls if call[0] == "startSustainedNote"], [], calls)
        self.assertEqual([call[0] for call in calls if call[0] == "physical.noteOff"], [], calls)
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
          window.__mockExquisInput.onmidimessage({ data: [0x82, 48, 0] });
          window.__mockExquisInput.onmidimessage({ data: [0x8E, 52, 0] });
          window.__mockExquisInput.onmidimessage({ data: [0x8C, 55, 0] });
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
        self.page.wait_for_timeout(80)
        mid_hold = self.page.evaluate("""
        () => ({
          debug: window.__exquisDebugSnapshot(),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent,
          starts: window.__ssliCalls.filter(call => call[0] === 'physical.noteOn'),
          physicalOff: window.__ssliCalls.filter(call => call[0] === 'physical.noteOff')
        })
        """)
        self.assertEqual(mid_hold["debug"]["heldNotes"], 1, mid_hold)
        self.assertEqual(mid_hold["debug"]["midiVoices"], 0, mid_hold)
        self.assertEqual(mid_hold["starts"], [], mid_hold)
        self.assertNotIn("after-one-shot-expire B2 held=1 local=0", mid_hold["log"])
        self.assertEqual(mid_hold["physicalOff"], [], mid_hold)
        self.page.evaluate("""
        () => {
          const input = window.__mockExquisInput;
          input.onmidimessage({ data: [0xD2, 0] });
          input.onmidimessage({ data: [0x82, 47, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 1")
        self.page.wait_for_timeout(1750)
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
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 1")
        self.page.wait_for_timeout(230)
        metrics = self.page.evaluate("""
        () => ({
          starts: window.__ssliCalls.filter(call => call[0] === 'physical.noteOn'),
          stops: window.__ssliCalls.filter(call => call[0] === 'stopSustainedNote'),
          physicalOff: window.__ssliCalls.filter(call => call[0] === 'physical.noteOff'),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual([call[1] for call in metrics["starts"]], [48], metrics)
        self.assertEqual(metrics["stops"], [], metrics)
        self.assertEqual(metrics["physicalOff"], [], metrics)
        self.assertIn("articulation queued C3 mode=release-strum", metrics["log"])
        self.assertIn("articulation flush mode=release-strum", metrics["log"])

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
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 1")
        self.page.wait_for_timeout(230)
        metrics = self.page.evaluate("""
        () => ({
          starts: window.__ssliCalls.filter(call => call[0] === 'physical.noteOn'),
          sustained: window.__ssliCalls.filter(call => call[0] === 'startSustainedNote'),
          physicalOff: window.__ssliCalls.filter(call => call[0] === 'physical.noteOff'),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual([call[1] for call in metrics["starts"]], [52], metrics)
        self.assertEqual(metrics["sustained"], [], metrics)
        self.assertEqual(metrics["physicalOff"], [], metrics)
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
        self.page.wait_for_function("() => window.__ssliCalls.filter(call => call[0] === 'physical.noteOn').length >= 1")
        self.page.wait_for_timeout(230)
        metrics = self.page.evaluate("""
        () => ({
          starts: window.__ssliCalls.filter(call => call[0] === 'physical.noteOn'),
          sustained: window.__ssliCalls.filter(call => call[0] === 'startSustainedNote'),
          physicalOff: window.__ssliCalls.filter(call => call[0] === 'physical.noteOff'),
          log: document.querySelector('[data-testid="diagnostic-log"]').textContent
        })
        """)
        self.assertEqual([call[1] for call in metrics["starts"]], [52], metrics)
        self.assertEqual(metrics["sustained"], [], metrics)
        self.assertEqual(metrics["physicalOff"], [], metrics)
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

    def test_regression_midi_duplicate_note_illuminates_all_matching_physical_cells(self):
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
        self.page.evaluate("() => window.__mockExquisInput.onmidimessage({ data: [0x9F, 60, 96] })")
        self.page.wait_for_function("() => document.querySelectorAll('.midi-held').length === 2")
        held = self.page.locator(".midi-held")
        self.assertEqual(sorted(held.evaluate_all("elements => elements.map((element) => element.getAttribute('data-cell-id'))")), ["r1c1", "r2c5"])

    def test_regression_midi_duplicate_note_keeps_hardware_identity_ambiguous(self):
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
        self.page.wait_for_function("() => document.querySelectorAll('.midi-held').length === 2")
        snapshot = self.page.evaluate("() => window.__exquisDebugSnapshot()")
        self.assertEqual(snapshot["lastMidi"]["cellId"], "", snapshot)
        self.assertEqual(snapshot["lastMidi"]["cellIds"], ["r1c1", "r2c5"], snapshot)

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
        self.assertEqual(expression_calls[-1], ["setExpression", 7779, 0.756], calls)
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
        self.assertIn(["setExpression", 900, 0], calls)
        self.assertNotIn(["clearExpression"], calls)
        self.assertEqual(len([call for call in calls if call[0] == "setExpression" and call[1] == 7850]), 1, calls)
        self.assertGreater(calls.index(["setExpression", 900, 0]), 1, calls)
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

    def test_regression_low_velocity_aftertouch_lifts_actual_subtractive_audio(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_subtractive_low_velocity_pressure_sweep"
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
                "--pressure-sweep-velocity",
                "12",
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
        self.assertEqual(int(signature["velocity"]), 12, row)
        self.assertGreater(float(signature["lowRms"]), 0.001, row)
        self.assertGreater(float(signature["highRms"]), 0.065, row)
        self.assertGreater(float(signature["rmsRatio"]), 6.0, row)
        self.assertIn("SSLI expression pressure=120", signature["diagnosticLog"])
        self.assertIn("interaction=pressure-swell", signature["diagnosticLog"])
        self.assertIn("SSLI MIDI sustain start C3 velocity=127 pressure=12", signature["diagnosticLog"])
        self.assertIn("SSLI expression pressure=120 cutoff=9498Hz gain=0.94 interaction=pressure-swell", signature["diagnosticLog"])

    def test_regression_three_note_pad_pressure_zero_recovers_actual_audio(self):
        output_dir = ROOT / "tmp_preset_sweep_unittest_subtractive_pad_chord_pressure_recovery"
        result = subprocess.run(
            [
                "python",
                "tools/preset_sweep.py",
                "--no-build",
                "--engine",
                "Subtractive",
                "--category",
                "Pads",
                "--preset-contains",
                "Atmosphere",
                "--trigger",
                "chord-pressure-recovery-midi",
                "--audio-sample-ms",
                "1200",
                "--output-dir",
                str(output_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=180,
        )
        payload = json.loads((output_dir / "preset-sweep-results.json").read_text(encoding="utf-8"))
        row = next(item for item in payload["results"] if item["presetLabel"] == "Atmosphere")
        signature = row["audioSignature"]
        self.assertEqual(result.returncode, 0, f"row={json.dumps(row, indent=2)}\nstdout={result.stdout}\nstderr={result.stderr}")
        self.assertEqual(signature["notes"], [48, 52, 55], row)
        self.assertGreater(float(signature["high1Rms"]), 0.05, row)
        self.assertGreater(float(signature["high2Rms"]), 0.05, row)
        self.assertGreater(float(signature["high2ToHigh1Ratio"]), 0.75, row)
        self.assertGreater(float(signature["high2ToZeroRatio"]), 2.5, row)
        self.assertIn("SSLI expression pressure=0", signature["diagnosticLog"])
        self.assertIn("SSLI expression pressure=120", signature["diagnosticLog"])

    def test_regression_plucked_interaction_does_not_apply_low_velocity_pressure_swell(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 12] });
        }
        """)
        self.page.wait_for_timeout(80)
        self.assertEqual(self.page.evaluate("() => window.__exquisDebugSnapshot().midiVoices"), 0)
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0xA1, 48, 120] });
          window.__mockExquisInput.onmidimessage({ data: [0x81, 48, 0] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.some(call => call[0] === 'physical.noteOn')")
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual([call for call in calls if call[0] == "physical.updateNotePressure"], [], calls)
        self.assertEqual([call for call in calls if call[0] == "setExpression"], [], calls)
        self.assertEqual([call[1] for call in calls if call[0] == "physical.noteOn"], [48], calls)

    def test_regression_repeated_plucked_pressure_never_enters_live_swell_path(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Plucked")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Nylon Guitar")
        self.install_articulation_mock("physical", "pluck")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        async () => {
          const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));
          for (let i = 0; i < 8; i += 1) {
            const midi = 48 + (i % 3) * 2;
            const channel = (i % 6) + 1;
            window.__mockExquisInput.onmidimessage({ data: [0x90 | channel, midi, 10 + i] });
            await wait(35);
            for (const pressure of [0, 32, 96, 127, 14, 118]) {
              window.__mockExquisInput.onmidimessage({ data: [0xA0 | channel, midi, pressure] });
              await wait(4);
            }
            window.__mockExquisInput.onmidimessage({ data: [0x80 | channel, midi, 0] });
            await wait(35);
          }
        }
        """)
        self.page.wait_for_timeout(1200)
        calls = self.page.evaluate("() => window.__ssliCalls")
        self.assertEqual([call for call in calls if call[0] == "setExpression"], [], calls)
        self.assertEqual([call for call in calls if call[0] == "physical.updateNotePressure"], [], calls)
        self.assertGreaterEqual(len([call for call in calls if call[0] == "physical.noteOn"]), 1, calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("articulation flush mode=release-strum", log)
        self.assertNotIn("cancelled release pluck on transition", log)
        self.assertNotIn("interaction=pressure-swell", log)

    def test_regression_struck_interaction_does_not_apply_low_velocity_pressure_swell(self):
        self.open_audio_drawer()
        self.page.select_option('[data-testid="sound-engine-select"]', "physical")
        self.page.select_option('[data-testid="sound-category-select"]', label="Struck")
        self.page.select_option('[data-testid="sound-preset-select"]', label="Marimba")
        self.install_articulation_mock("physical", "strike")
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__mockExquisInput && window.__mockExquisInput.onmidimessage")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0x91, 48, 12] });
        }
        """)
        self.page.wait_for_function("() => window.__ssliCalls.some(call => call[0] === 'startSustainedNote')")
        self.page.evaluate("""
        () => {
          window.__mockExquisInput.onmidimessage({ data: [0xA1, 48, 120] });
        }
        """)
        self.page.wait_for_timeout(80)
        calls = self.page.evaluate("() => window.__ssliCalls")
        expression_calls = [call for call in calls if call[0] == "setExpression"]
        self.assertEqual([call for call in calls if call[0] == "physical.updateNotePressure"], [], calls)
        self.assertTrue(all(call[2] <= 1.1 for call in expression_calls), calls)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertIn("SSLI struck pressure ignored after onset C3", log)
        self.assertNotIn("gain=5.00 interaction=pressure-swell", log)

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
        self.assertIn(["setInstrumentVolume", 0, 100], calls)
        self.assertTrue(any(call[0] == "startSustainedNote" and call[1] == 48 and call[2] == 127 and call[3] == 100 and call[4] == 1 for call in calls), calls)
        self.page.wait_for_timeout(80)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertNotIn("SSLI normalization output preset=" + celesta_value, log)
        self.assertIn("SSLI normalization preset=" + celesta_value + " volume=100 output=1.00", log)

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
        self.assertIn(["setInstrumentVolume", 0, 100], calls)
        self.assertTrue(any(call[0] == "startSustainedNote" and call[1] == 48 and call[2] == 127 and call[3] == 100 and call[4] == 1 for call in calls), calls)
        self.page.wait_for_timeout(80)
        log = self.page.locator('[data-testid="diagnostic-log"]').inner_text()
        self.assertNotIn("SSLI normalization output preset=" + rhodes_value, log)
        self.assertIn("SSLI normalization preset=" + rhodes_value + " volume=100 output=1.00", log)

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
        self.assertIn(["startSustainedNote", 48, 127], calls)
        expression_calls = [call for call in calls if call[0] == "setExpression"]
        self.assertGreaterEqual(len(expression_calls), 1, calls)
        self.assertIn(["setExpression", 10000, 1], expression_calls)
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
        self.assertTrue(all(call[2] <= 5 for call in expression_calls), calls)
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
        self.page.once("dialog", lambda dialog: dialog.accept())
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
        self.open_audio_drawer()
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
        self.open_audio_drawer()
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
        self.open_audio_drawer()
        self.assertTrue(self.page.locator('[data-testid="sound-engine-select"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="sound-category-select"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="sound-preset-select"]').is_visible())
        self.page.select_option('[data-testid="sound-engine-select"]', "subtractive")
        self.page.select_option('[data-testid="sound-category-select"]', "Keys")
        self.assertIn("Wurlitzer EP", self.page.locator('[data-testid="sound-preset-select"]').inner_text())

    def test_regression_fx_chain_selectors_are_hierarchical(self):
        self.open_audio_drawer()
        self.assertTrue(self.page.locator('[data-testid="fx-category-select"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="fx-preset-select"]').is_visible())
        self.page.select_option('[data-testid="fx-category-select"]', "Performance / Live")
        self.assertIn("Lead Solo", self.page.locator('[data-testid="fx-preset-select"]').inner_text())

    def test_regression_fx_controls_share_one_visual_row(self):
        self.open_audio_drawer()
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
        self.open_hardware_tools()
        self.page.locator('[data-testid="hardware-diagnostics"]').click()
        self.assertTrue(self.page.locator('[data-testid="console-panel"]').is_visible())
        self.assertEqual(self.page.locator('[data-testid="reset-console"]').count(), 1)
        self.assertEqual(self.page.locator('[data-testid="copy-console"]').count(), 1)
        self.assertEqual(self.page.locator('[data-testid="exit-console"]').count(), 1)
        self.assertEqual(self.page.locator('[data-testid="exit-console"]').inner_text(), "Collapse")
        self.assertTrue(self.page.locator('[data-testid="diagnostic-log"]').is_visible())
        self.page.locator('[data-testid="audio-diag"]').click()
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"diagnostic-log\"]').textContent.includes('audio')")
        expanded_height = self.page.locator('[data-testid="diagnostic-log"]').bounding_box()["height"]
        self.assertGreaterEqual(expanded_height, 180)
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.locator('[data-testid="reset-console"]').click()
        self.assertEqual(self.page.locator('[data-testid="diagnostic-log"]').inner_text(), "Ready.")
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
        self.assertGreaterEqual(side["y"], stage["y"] + stage["height"] + 4)
        self.assertLessEqual(abs(stage["x"] - side["x"]), 1)
        self.assertLessEqual(abs((stage["x"] + stage["width"]) - (side["x"] + side["width"])), 1)
        self.assertLessEqual(side["height"], 120)
        self.assertGreater(device_width / stage["width"], 0.8)
        self.assertGreater(keyboard["height"], 330)
        self.assertLessEqual(page_scroll_y, 1)

    def test_regression_exquis_ui_is_visually_dominant(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        stage = self.page.locator(".stage-panel").bounding_box()
        keyboard = self.page.locator('[data-testid="keyboard"]').bounding_box()
        top = self.page.locator('[data-testid="edge-top-controls"]').bounding_box()
        bottom = self.page.locator('[data-testid="edge-bottom-controls"]').bounding_box()
        device_width = max(top["x"] + top["width"], keyboard["x"] + keyboard["width"], bottom["x"] + bottom["width"]) - min(top["x"], keyboard["x"], bottom["x"])
        self.assertGreaterEqual(device_width / stage["width"], 0.78)
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
        if metrics["top"]["width"] and metrics["bottom"]["width"]:
            self.assertLess(metrics["bottom"]["right"], metrics["keyboard"]["left"], metrics)
            self.assertGreater(metrics["top"]["left"], metrics["keyboard"]["right"], metrics)
        self.assertGreaterEqual(metrics["fieldWidth"], 620, metrics)
        self.assertGreaterEqual(metrics["fieldHeight"], 360, metrics)
        self.assertLessEqual(metrics["pageY"], 1)

    def test_regression_practice_audio_has_no_legacy_guide_tone_selector(self):
        self.assertEqual(self.page.locator('[data-testid="tone-select"]').count(), 0)
        self.assertEqual(self.page.locator('.guide-section').count(), 0)
        self.assertTrue(self.page.locator('[data-testid="sound-engine-select"]').is_visible())

    def test_regression_practice_coach_is_the_authoritative_learning_surface(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        coach = self.page.locator('[data-testid="practice-coach"]')
        self.assertTrue(coach.is_visible())
        for test_id in [
            "coach-now-playing",
            "coach-action-cue",
            "coach-result",
            "coach-next-action",
            "coach-progress",
        ]:
            field = coach.locator(f'[data-testid="{test_id}"]')
            self.assertTrue(field.is_visible(), test_id)
        self.assertEqual(coach.locator('[data-testid="coach-result"]').count(), 1)
        self.assertEqual(coach.locator('[data-testid="coach-progress"]').count(), 1)
        self.assertEqual(coach.locator('[data-testid="coach-result"]').get_attribute("role"), "status")
        self.assertEqual(coach.locator('[data-testid="coach-result"]').get_attribute("aria-live"), "polite")
        self.assertFalse(self.page.locator('[data-testid="midi-activity"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="last-midi"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="console-panel"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="calibration-section"]').is_visible())

    def test_regression_session_settings_uses_a_specific_learner_facing_label(self):
        settings = self.page.locator('[data-testid="practice-tools"]')
        self.assertEqual(settings.locator('summary').inner_text(), 'Session settings')
        self.assertFalse(settings.evaluate('el => el.open'))

    def test_regression_practice_coach_outcome_names_the_next_action(self):
        self.page.evaluate("""
        () => {
          window.__practiceCoachInput = { id: 'practice-coach', name: 'Practice Coach Input', manufacturer: 'Intuitive Instruments', onmidimessage: null };
          navigator.requestMIDIAccess = () => Promise.resolve({
            inputs: { forEach: (cb) => cb(window.__practiceCoachInput) },
            outputs: { forEach: () => {} },
            onstatechange: null
          });
        }
        """)
        self.page.locator('[data-testid="enable-midi"]').click()
        self.page.wait_for_function("() => window.__practiceCoachInput && window.__practiceCoachInput.onmidimessage")
        target_midi = self.page.locator('.key.current').get_attribute('data-midi')
        self.page.evaluate("(midi) => window.__practiceCoachInput.onmidimessage({ data: [0x90, Number(midi), 100] })", target_midi)
        self.page.wait_for_function("() => document.querySelector('[data-testid=\"coach-result\"]').textContent.includes('Correct:')")
        result = self.page.locator('[data-testid="coach-result"]').inner_text()
        next_action = self.page.locator('[data-testid="coach-next-action"]').inner_text()
        self.assertIn("Correct:", result)
        self.assertIn("Continue", next_action)
        self.assertIn("Score:", self.page.locator('[data-testid="coach-progress"]').inner_text())
        self.assertIn("Step", self.page.locator('[data-testid="coach-progress"]').inner_text())

    def test_regression_no_scroll_layout_does_not_clip_right_rail(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""() => {
          const side = document.querySelector('.side-panel');
          return {
            pageX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
            pageY: document.documentElement.scrollHeight - document.documentElement.clientHeight,
            sideOverflow: side.scrollHeight - side.clientHeight,
            sideOverflowCss: getComputedStyle(side).overflow,
            sideHeight: side.getBoundingClientRect().height
          };
        }""")
        self.assertLessEqual(metrics["pageX"], 1)
        self.assertLessEqual(metrics["pageY"], 1)
        self.assertEqual(metrics["sideOverflowCss"], "hidden")
        self.assertLessEqual(metrics["sideHeight"], 120)

    def test_regression_laptop_no_scroll_keeps_primary_controls_visible(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""() => {
          const selectors = [
            '[data-testid="orientation-select"]',
            '[data-testid="rotate-surface"]',
            '[data-testid="practice-coach"]',
            '[data-testid="coach-now-playing"]',
            '[data-testid="coach-action-cue"]',
            '[data-testid="coach-result"]',
            '[data-testid="coach-next-action"]',
            '[data-testid="coach-progress"]',
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

    def test_regression_practice_coach_is_first_prominent_side_rail_surface(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""() => {
          const side = document.querySelector('.side-panel').getBoundingClientRect();
          const coach = document.querySelector('[data-testid="practice-coach"]');
          const enable = document.querySelector('[data-testid="enable-midi"]').getBoundingClientRect();
          const nowPlaying = document.querySelector('[data-testid="coach-now-playing"]').getBoundingClientRect();
          return {
            sideTop: side.top,
            coachIndex: Array.from(document.querySelector('.side-panel').children).indexOf(coach),
            coachTop: coach.getBoundingClientRect().top,
            enableTop: enable.top,
            enableHeight: enable.height,
            nowPlayingTop: nowPlaying.top,
            enableText: document.querySelector('[data-testid="enable-midi"]').textContent.trim()
          };
        }""")
        self.assertEqual(metrics["coachIndex"], 0)
        self.assertLess(metrics["coachTop"] - metrics["sideTop"], 24)
        self.assertLess(metrics["enableTop"], metrics["nowPlayingTop"])
        self.assertGreaterEqual(metrics["enableHeight"], 44)
        self.assertIn("Enable MIDI", metrics["enableText"])

    def test_regression_practice_coach_status_regions_remain_visible_and_live_on_laptop(self):
        self.page.set_viewport_size({"width": 1366, "height": 768})
        metrics = self.page.evaluate("""() => {
          const selectors = [
            '[data-testid="midi-status"]',
            '[data-testid="coach-result"]',
            '[data-testid="coach-progress"]'
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
        for item in metrics[:2]:
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

    def test_regression_ipad_shell_prioritizes_playing_canvas_over_setup_controls(self):
        self.page.set_viewport_size({"width": 1024, "height": 768})
        metrics = self.page.evaluate("""() => {
          const box = (selector) => document.querySelector(selector).getBoundingClientRect().toJSON();
          const keyboard = box('[data-testid="keyboard"]');
          return {
            top: box('.top-panel'),
            stage: box('.stage-panel'),
            coach: box('.side-panel'),
            keyboard,
            overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
            vertical: document.documentElement.scrollHeight - document.documentElement.clientHeight
          };
        }""")
        self.assertFalse(self.page.locator('.side-panel').is_visible())
        self.assertGreaterEqual(metrics["keyboard"]["width"] / metrics["stage"]["width"], 0.94, metrics)
        self.assertGreaterEqual(metrics["keyboard"]["height"] / metrics["stage"]["height"], 0.8, metrics)
        self.assertGreater(metrics["stage"]["height"], metrics["top"]["height"] * 4, metrics)
        self.assertLessEqual(metrics["stage"]["bottom"], 768, metrics)
        self.assertLessEqual(metrics["overflow"], 1, metrics)
        self.assertLessEqual(metrics["vertical"], 1, metrics)
        self.page.locator('[data-testid="workspace-setup"]').click()
        self.assertTrue(self.page.locator('[data-testid="setup-workspace"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="exercise-family-select"]').is_visible())
        self.page.locator('[data-testid="workspace-practice"]').click()
        self.page.locator('[data-testid="coach-toggle"]').click()
        self.assertTrue(self.page.locator('.side-panel').is_visible())

    def test_regression_practice_surface_uses_its_available_canvas(self):
        for width, height in [(1024, 768), (1366, 768), (1600, 900)]:
            with self.subTest(viewport=(width, height)):
                self.page.set_viewport_size({"width": width, "height": height})
                self.page.wait_for_function("""() => {
                  const surface = document.querySelector('[data-testid="practice-surface"]').getBoundingClientRect();
                  const keys = [...document.querySelectorAll('[data-testid="exquis-key"]')].map((key) => key.getBoundingClientRect());
                  const field = {
                    left: Math.min(...keys.map((box) => box.left)),
                    right: Math.max(...keys.map((box) => box.right)),
                    top: Math.min(...keys.map((box) => box.top)),
                    bottom: Math.max(...keys.map((box) => box.bottom))
                  };
                  return field.right - field.left >= surface.width * 0.68
                    && field.bottom - field.top >= surface.height * 0.90;
                }""")
                metrics = self.page.evaluate("""() => {
                  const surface = document.querySelector('[data-testid="practice-surface"]').getBoundingClientRect();
                  const keys = [...document.querySelectorAll('[data-testid="exquis-key"]')].map((key) => key.getBoundingClientRect());
                  const field = {
                    left: Math.min(...keys.map((box) => box.left)),
                    right: Math.max(...keys.map((box) => box.right)),
                    top: Math.min(...keys.map((box) => box.top)),
                    bottom: Math.max(...keys.map((box) => box.bottom))
                  };
                  field.width = field.right - field.left;
                  field.height = field.bottom - field.top;
                  return {
                    viewport: { width: window.innerWidth, height: window.innerHeight },
                    surface: surface.toJSON(),
                    field,
                    horizontalDeadSpace: 1 - field.width / surface.width,
                    verticalDeadSpace: 1 - field.height / surface.height
                  };
                }""")
                self.assertLessEqual(metrics["horizontalDeadSpace"], 0.32, metrics)
                self.assertLessEqual(metrics["verticalDeadSpace"], 0.10, metrics)

    def test_regression_workspaces_separate_practice_library_and_studio(self):
        self.page.set_viewport_size({"width": 1024, "height": 768})
        self.assertEqual(self.page.locator('.app-shell').get_attribute('data-workspace'), 'practice')
        self.assertTrue(self.page.locator('.stage-panel').is_visible())
        self.assertFalse(self.page.locator('.side-panel').is_visible())
        self.assertFalse(self.page.locator('[data-testid="library-workspace"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="studio-workspace"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="setup-workspace"]').is_visible())

        self.page.locator('[data-testid="workspace-setup"]').click()
        self.assertEqual(self.page.locator('.app-shell').get_attribute('data-workspace'), 'setup')
        self.assertTrue(self.page.locator('[data-testid="setup-workspace"]').is_visible())
        self.assertFalse(self.page.locator('.stage-panel').is_visible())
        self.assertEqual(
            self.page.locator('[data-testid="tonic-select"]').evaluate(
                "element => element.closest('#setupControlsSlot') !== null"
            ),
            True,
        )
        self.assertEqual(self.page.locator('[data-testid="workspace-setup"]').get_attribute('aria-pressed'), 'true')

        self.page.locator('[data-testid="workspace-library"]').click()
        self.assertEqual(self.page.locator('.app-shell').get_attribute('data-workspace'), 'library')
        self.assertEqual(self.page.locator('[data-testid="workspace-library"]').inner_text(), 'Exercises')
        self.assertTrue(self.page.locator('[data-testid="library-workspace"]').is_visible())
        self.assertFalse(self.page.locator('.stage-panel').is_visible())
        self.assertFalse(self.page.locator('.side-panel').is_visible())
        self.assertEqual(
            self.page.locator('[data-testid="exercise-family-select"]').evaluate(
                "element => element.closest('#libraryControlsSlot') !== null"
            ),
            True,
        )
        self.assertEqual(self.page.locator('[data-testid="workspace-library"]').get_attribute('aria-pressed'), 'true')

        self.page.locator('[data-testid="workspace-studio"]').click()
        self.assertEqual(self.page.locator('.app-shell').get_attribute('data-workspace'), 'studio')
        self.assertTrue(self.page.locator('[data-testid="studio-workspace"]').is_visible())
        self.assertEqual(self.page.locator('[data-testid="studio-hardware-tab"]').get_attribute('aria-pressed'), 'true')
        self.assertTrue(self.page.locator('[data-testid="enable-midi"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="sound-engine-select"]').is_visible())
        self.page.locator('[data-testid="studio-sound-tab"]').click()
        self.assertEqual(
            self.page.locator('[data-testid="sound-engine-select"]').evaluate(
                "element => element.closest('#studioControlsSlot') !== null"
            ),
            True,
        )
        self.assertEqual(self.page.locator('[data-testid="studio-sound-tab"]').get_attribute('aria-pressed'), 'true')
        self.assertEqual(self.page.locator('[data-testid="sound-voice-tab"]').get_attribute('aria-pressed'), 'true')
        self.assertTrue(self.page.locator('[data-testid="sound-engine-select"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="fx-control-row"]').is_visible())

        self.page.locator('[data-testid="sound-effects-tab"]').click()
        self.assertEqual(self.page.locator('[data-testid="sound-effects-tab"]').get_attribute('aria-pressed'), 'true')
        self.assertTrue(self.page.locator('[data-testid="fx-control-row"]').is_visible())
        self.assertTrue(self.page.locator('[data-testid="filter-cutoff"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="sound-engine-select"]').is_visible())

        self.page.locator('[data-testid="sound-performance-tab"]').click()
        self.assertEqual(self.page.locator('[data-testid="sound-performance-tab"]').get_attribute('aria-pressed'), 'true')
        self.assertTrue(self.page.locator('[data-testid="performance-volume"]').is_visible())
        self.assertFalse(self.page.locator('[data-testid="fx-control-row"]').is_visible())
        self.assertEqual(self.page.locator('[data-testid="workspace-studio"]').get_attribute('aria-pressed'), 'true')
        self.assertEqual(self.page.locator('[data-testid="workspace-library"]').get_attribute('aria-pressed'), 'false')

        self.page.locator('[data-testid="workspace-library"]').click()
        self.page.locator('[data-testid="start-library-session"]').click()
        self.assertEqual(self.page.locator('.app-shell').get_attribute('data-workspace'), 'practice')
        self.assertTrue(self.page.locator('.stage-panel').is_visible())
        self.assertFalse(self.page.locator('.side-panel').is_visible())
        self.assertEqual(
            self.page.locator('[data-testid="exercise-family-select"]').evaluate(
                "element => element.closest('#practiceWorkflowControls') !== null"
            ),
            True,
        )

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
        self.assertGreaterEqual(metrics["side"]["left"], metrics["stage"]["right"] + 4, metrics)
        self.assertLessEqual(abs(metrics["side"]["top"] - metrics["stage"]["top"]), 1, metrics)

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
