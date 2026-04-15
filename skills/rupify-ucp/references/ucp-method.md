# Use Case Point Method

## Formula

- `UAW`: weighted actor total
- `UUCW`: weighted use-case total
- `UUCP = UAW + UUCW`
- `TCF = 0.6 + (0.01 * TFactor)`
- `EF = 1.4 + (-0.03 * EFactor)`
- `UCP = UUCP * TCF * EF`
- `Effort Hours = UCP * productivity_hours_per_ucp`

## Actor Weights

- `simple = 1`
- `average = 2`
- `complex = 3`

## Use-Case Weights

- `simple = 5`
- `average = 10`
- `complex = 15`

## Technical Factor Weights

- `distributed_system = 2.0`
- `response_time = 1.0`
- `end_user_efficiency = 1.0`
- `complex_internal_processing = 1.0`
- `reusable_code = 1.0`
- `easy_to_install = 0.5`
- `easy_to_use = 0.5`
- `portability = 2.0`
- `easy_to_change = 1.0`
- `concurrency = 1.0`
- `special_security = 1.0`
- `third_party_access = 1.0`
- `special_user_training = 1.0`

## Environmental Factor Weights

- `familiar_with_process = 1.5`
- `application_experience = 0.5`
- `object_oriented_experience = 1.0`
- `lead_analyst_capability = 0.5`
- `motivation = 1.0`
- `stable_requirements = 2.0`
- `part_time_staff = -1.0`
- `difficult_programming_language = -1.0`

