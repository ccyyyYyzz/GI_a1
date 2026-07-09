# Stage 4 URED Trace Audit

APL URED minimum CNR gate used for this audit: `10.43`.

The audit separates final-output CNR from target-aware best-trace CNR.
Best-trace values are diagnostic upper bounds because they use the ground
truth target to choose a step; they are not deployable stopping rules.

## Best Sweep/Object Results

| sweep                                | object        | num_configs | best_final_cnr | best_final_config | best_trace_cnr | best_trace_config | best_trace_step | trace_hits_apl_min |
| ------------------------------------ | ------------- | ----------- | -------------- | ----------------- | -------------- | ----------------- | --------------- | ------------------ |
| stage4_ured_nlm_matched_soft_control | letter_A      | 5           | 9.1            | cfg0003           | 9.478          | cfg0003           | 13              | False              |
| stage4_ured_nlm_matched_soft_control | letter_L      | 5           | 15.96          | cfg0004           | 16.36          | cfg0004           | 14              | True               |
| stage4_ured_nlm_matched_soft_control | ring          | 5           | 10.05          | cfg0003           | 10.5           | cfg0003           | 13              | True               |
| stage4_ured_nlm_matched_soft_control | stripe_target | 5           | 7.337          | cfg0004           | 7.677          | cfg0004           | 13              | False              |

## Best Final Output Per Object

| object        | sweep                                | best_final_cnr | best_final_config | final_hits_apl_min | final_steps | final_nlm_h |
| ------------- | ------------------------------------ | -------------- | ----------------- | ------------------ | ----------- | ----------- |
| letter_A      | stage4_ured_nlm_matched_soft_control | 9.1            | cfg0003           | False              | 15          | 0.062       |
| letter_L      | stage4_ured_nlm_matched_soft_control | 15.96          | cfg0004           | True               | 15          | 0.062       |
| ring          | stage4_ured_nlm_matched_soft_control | 10.05          | cfg0003           | False              | 15          | 0.062       |
| stripe_target | stage4_ured_nlm_matched_soft_control | 7.337          | cfg0004           | False              | 15          | 0.062       |

## Best Target-Aware Trace Per Object

| object        | sweep                                | best_trace_cnr | best_trace_config | best_trace_step | trace_hits_apl_min |
| ------------- | ------------------------------------ | -------------- | ----------------- | --------------- | ------------------ |
| letter_A      | stage4_ured_nlm_matched_soft_control | 9.478          | cfg0003           | 13              | False              |
| letter_L      | stage4_ured_nlm_matched_soft_control | 16.36          | cfg0004           | 14              | True               |
| ring          | stage4_ured_nlm_matched_soft_control | 10.5           | cfg0003           | 13              | True               |
| stripe_target | stage4_ured_nlm_matched_soft_control | 7.677          | cfg0004           | 13              | False              |

## Interpretation

At least one object remains below the APL URED minimum even with target-aware trace selection: letter_A (9.48), stripe_target (7.68).
The final-output CNR remains lower than target-aware trace peaks, so any
paper-threshold claim still requires either a deployable stopping rule
or a stronger URED/SCGI reconstruction path.
