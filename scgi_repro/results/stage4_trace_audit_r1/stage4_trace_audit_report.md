# Stage 4 URED Trace Audit

APL URED minimum CNR gate used for this audit: `10.43`.

The audit separates final-output CNR from target-aware best-trace CNR.
Best-trace values are diagnostic upper bounds because they use the ground
truth target to choose a step; they are not deployable stopping rules.

## Best Sweep/Object Results

| sweep                  | object        | num_configs | best_final_cnr | best_final_config | best_trace_cnr | best_trace_config | best_trace_step | trace_hits_apl_min |
| ---------------------- | ------------- | ----------- | -------------- | ----------------- | -------------- | ----------------- | --------------- | ------------------ |
| nlm_allobjects         | letter_A      | 2           | 8.453          | cfg0001           | 13.21          | cfg0001           | 117             | True               |
| nlm_allobjects         | letter_L      | 2           | 12.8           | cfg0000           | 21.11          | cfg0000           | 40              | True               |
| nlm_allobjects         | ring          | 2           | 7.842          | cfg0001           | 14.3           | cfg0001           | 64              | True               |
| nlm_microrefine_stripe | stripe_target | 72          | 9.365          | cfg0023           | 9.365          | cfg0059           | 36              | False              |
| nlm_refine_stripe      | stripe_target | 81          | 9.024          | cfg0022           | 9.214          | cfg0052           | 36              | False              |
| nlm_allobjects         | stripe_target | 2           | 6.033          | cfg0001           | 8.932          | cfg0000           | 40              | False              |
| nlm_earlystop_stripe   | stripe_target | 40          | 8.932          | cfg0006           | 8.932          | cfg0026           | 40              | False              |
| nlm_stripe             | stripe_target | 48          | 5.131          | cfg0040           | 8.913          | cfg0040           | 38              | False              |
| nlm_deeper_stripe      | stripe_target | 18          | 5.637          | cfg0007           | 8.52           | cfg0005           | 327             | False              |

## Best Final Output Per Object

| object        | sweep                  | best_final_cnr | best_final_config | final_hits_apl_min | final_steps | final_nlm_h |
| ------------- | ---------------------- | -------------- | ----------------- | ------------------ | ----------- | ----------- |
| letter_A      | nlm_allobjects         | 8.453          | cfg0001           | False              | 200         | 0.08        |
| letter_L      | nlm_allobjects         | 12.8           | cfg0000           | True               | 200         | 0.06        |
| ring          | nlm_allobjects         | 7.842          | cfg0001           | False              | 200         | 0.08        |
| stripe_target | nlm_microrefine_stripe | 9.365          | cfg0023           | False              | 36          | 0.062       |

## Best Target-Aware Trace Per Object

| object        | sweep                  | best_trace_cnr | best_trace_config | best_trace_step | trace_hits_apl_min |
| ------------- | ---------------------- | -------------- | ----------------- | --------------- | ------------------ |
| letter_A      | nlm_allobjects         | 13.21          | cfg0001           | 117             | True               |
| letter_L      | nlm_allobjects         | 21.11          | cfg0000           | 40              | True               |
| ring          | nlm_allobjects         | 14.3           | cfg0001           | 64              | True               |
| stripe_target | nlm_microrefine_stripe | 9.365          | cfg0059           | 36              | False              |

## Interpretation

At least one object remains below the APL URED minimum even with target-aware trace selection: stripe_target (9.36).
The final-output CNR remains lower than target-aware trace peaks, so any
paper-threshold claim still requires either a deployable stopping rule
or a stronger URED/SCGI reconstruction path.
