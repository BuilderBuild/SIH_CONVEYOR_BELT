# ConveyX final test report

Continuation verified 24 October 2026: **51 passed in CPU and 51 passed in CUDA**, zero failures/errors/skips. One upstream pandas deprecation warning per run. Two final GPU dashboard regression tests also passed after the deployment-review display update.

CPU JUnit: outputs/reports/tests_cpu.xml. GPU JUnit: outputs/reports/tests_gpu.xml. Final dashboard JUnit: outputs/reports/dashboard_gpu_final.xml.

| Test | CPU | CUDA |
|---|---|---|
| test_invalid_labels[1 .5 .5 .2 .2] | Passed | Passed |
| test_invalid_labels[0 nan .5 .2 .2] | Passed | Passed |
| test_invalid_labels[0 .5 .5 0 .2] | Passed | Passed |
| test_invalid_labels[0 .95 .5 .2 .2] | Passed | Passed |
| test_invalid_labels[0 .5 .5] | Passed | Passed |
| test_invalid_labels[0 2 .5 .2 .2] | Passed | Passed |
| test_invalid_labels[0 .5 .5 .2 -1] | Passed | Passed |
| test_empty_and_valid_labels | Passed | Passed |
| test_dataset_audit_catches_content_leakage_and_missing_labels | Passed | Passed |
| test_database_idempotence_filters_and_alerts | Passed | Passed |
| test_temporal_alerts_consecutive_hits_repeat_suppression_expiry | Passed | Passed |
| test_temporal_filter_resets_missed_frame | Passed | Passed |
| test_one_to_one_box_matching | Passed | Passed |
| test_model_loading_and_real_image | Passed | Passed |
| test_invalid_inference_input[None] | Passed | Passed |
| test_invalid_inference_input[does-not-exist.png] | Passed | Passed |
| test_invalid_inference_input[source2] | Passed | Passed |
| test_invalid_inference_input[source3] | Passed | Passed |
| test_invalid_inference_input[source4] | Passed | Passed |
| test_invalid_checkpoints_and_config | Passed | Passed |
| test_real_video_processing_streamed | Passed | Passed |
| test_invalid_video_releases_capture | Passed | Passed |
| test_camera_disconnection_releases_and_logs | Passed | Passed |
| test_camera_stop_releases_capture | Passed | Passed |
| test_save_image_does_not_overwrite | Passed | Passed |
| test_overlap_suppression_keeps_one_region_per_overlapping_pair | Passed | Passed |
| test_generic_pretrained_checkpoint_rejected | Passed | Passed |
| test_training_stops_before_model_load_on_current_leakage | Passed | Passed |
| test_heldout_test_requires_explicit_flag | Passed | Passed |
| test_invalid_device_rejected | Passed | Passed |
| test_normal_labels_and_orphans_flagged | Passed | Passed |
| test_dashboard_all_pages_launch | Passed | Passed |
| test_camera_start_stop_updates_buttons_without_duplicate_workers | Passed | Passed |
| test_derivation_excludes_duplicates_without_reassignment_or_source_changes | Passed | Passed |
| test_derivation_refuses_existing_destination | Passed | Passed |
| test_conflicting_duplicate_annotations_abort_before_copy | Passed | Passed |
| test_duplicate_test_content_is_preserved_and_excluded_from_training | Passed | Passed |
| test_duplicate_members_within_test_require_review | Passed | Passed |
| test_comparison_uses_scores_not_report_recency | Passed | Passed |
| test_incomparable_reports_cannot_promote[change0] | Passed | Passed |
| test_incomparable_reports_cannot_promote[change1] | Passed | Passed |
| test_incomparable_reports_cannot_promote[change2] | Passed | Passed |
| test_incomparable_reports_cannot_promote[change3] | Passed | Passed |
| test_incomparable_reports_cannot_promote[change4] | Passed | Passed |
| test_changed_checkpoint_cannot_be_promoted | Passed | Passed |
| test_operating_point_guard_catches_regressions[45-84-False] | Passed | Passed |
| test_operating_point_guard_catches_regressions[40-85-False] | Passed | Passed |
| test_operating_point_guard_catches_regressions[40-83-True] | Passed | Passed |
| test_operating_point_guard_catches_regressions[39-84-True] | Passed | Passed |
| test_training_writes_provenance_and_unique_experiments | Passed | Passed |
| test_training_failure_persisted_and_not_hidden | Passed | Passed |

Real-checkpoint verification additionally covers 100 GPU training epochs, eight matched validation runs, final held-out evaluation, actual CUDA computation, GPU image/video/database smoke and 115-frame physical camera capture with stop/release.

All 333 original active-dataset image/label/YAML hashes and original checkpoint hashes matched preservation records. See outputs/reports/preservation_verification.json.

The original dataset audit still intentionally fails because originals are preserved. The separate verified dataset passes with no exact duplicates/leakage. Videos in the smoke test repeat a real project image, not independent real belt motion.

The initial pre-epoch native YAML-path failure was fixed. Earlier prototype verification history is preserved in docs/TEST_REPORT.prototype_v1.md. No production detection-quality or hardware-control certification is claimed.
