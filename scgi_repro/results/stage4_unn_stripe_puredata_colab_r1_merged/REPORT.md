# Stage4 SCGI-UNN Stripe Pure-Data Colab r1

- rows: 96 / 96
- successful Colab shard artifacts: 2 / 2
- source ref: `4150e332d1be4c7a7e975856b298b8f33fb0fe1b`
- best final CNR: 2.547078
- best trace CNR: 2.550108
- APL UNN min CNR gate: 7.93
- passed final gate: False
- passed trace gate: False

This sweep isolates the SCGI-UNN-like pure data-fidelity route on the binding `stripe_target`: `beta=0`, `denoiser=none`, `xi in {0,0.01}`, 25-200 steps, multiple learning rates and TinyNAFNet capacities, fixed initialization seed 20240709. It expands the previous eight-row UNN evidence to 96 Colab rows and still remains near the SCGI baseline rather than the APL UNN range.

Top final-CNR records:

| source_import                                      | config_id   |   global_config_index |   steps |     lr |   beta |   xi |   x_step |   channels |   blocks |   residual_scale | denoiser   |     cnr |    psnr |   best_trace_cnr |   final_loss |
|:---------------------------------------------------|:------------|----------------------:|--------:|-------:|-------:|-----:|---------:|-----------:|---------:|-----------------:|:-----------|--------:|--------:|-----------------:|-------------:|
| pro1_stage4_unn_stripe_puredata_colab_r1_shard0of2 | cfg0040     |                    40 |      50 | 0.002  |      0 | 0    |      0.1 |         24 |        3 |             0.05 | none       | 2.54708 | 7.46908 |          2.54708 |  0.00020974  |
| pro1_stage4_unn_stripe_puredata_colab_r1_shard0of2 | cfg0044     |                    44 |      50 | 0.002  |      0 | 0.01 |      0.1 |         24 |        3 |             0.05 | none       | 2.54228 | 7.48197 |          2.54228 |  0.000210798 |
| pro1_stage4_unn_stripe_puredata_colab_r1_shard0of2 | cfg0056     |                    56 |     100 | 0.001  |      0 | 0    |      0.1 |         24 |        3 |             0.05 | none       | 2.54111 | 7.46187 |          2.5491  |  0.000206739 |
| pro1_stage4_unn_stripe_puredata_colab_r1_shard0of2 | cfg0060     |                    60 |     100 | 0.001  |      0 | 0.01 |      0.1 |         24 |        3 |             0.05 | none       | 2.54046 | 7.45901 |          2.54635 |  0.000207572 |
| pro1_stage4_unn_stripe_puredata_colab_r1_shard0of2 | cfg0076     |                    76 |     200 | 0.0005 |      0 | 0.01 |      0.1 |         24 |        3 |             0.05 | none       | 2.52049 | 7.44481 |          2.54368 |  0.000205848 |
| pro1_stage4_unn_stripe_puredata_colab_r1_shard0of2 | cfg0016     |                    16 |      25 | 0.002  |      0 | 0    |      0.1 |         24 |        3 |             0.05 | none       | 2.51987 | 7.45119 |          2.51987 |  0.000219753 |
| pro1_stage4_unn_stripe_puredata_colab_r1_shard0of2 | cfg0020     |                    20 |      25 | 0.002  |      0 | 0.01 |      0.1 |         24 |        3 |             0.05 | none       | 2.51985 | 7.45677 |          2.51985 |  0.000220393 |
| pro1_stage4_unn_stripe_puredata_colab_r1_shard0of2 | cfg0072     |                    72 |     200 | 0.0005 |      0 | 0    |      0.1 |         24 |        3 |             0.05 | none       | 2.5194  | 7.44646 |          2.54446 |  0.000205129 |
| pro1_stage4_unn_stripe_puredata_colab_r1_shard0of2 | cfg0032     |                    32 |      50 | 0.001  |      0 | 0    |      0.1 |         24 |        3 |             0.05 | none       | 2.51817 | 7.46812 |          2.51817 |  0.000219311 |
| pro1_stage4_unn_stripe_puredata_colab_r1_shard0of2 | cfg0036     |                    36 |      50 | 0.001  |      0 | 0.01 |      0.1 |         24 |        3 |             0.05 | none       | 2.51812 | 7.46522 |          2.51812 |  0.000219672 |
