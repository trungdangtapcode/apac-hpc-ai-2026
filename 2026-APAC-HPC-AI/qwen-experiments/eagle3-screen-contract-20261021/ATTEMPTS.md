# Validator correction during CPU preparation

The first local validate.py execution failed an assertion expecting reference
222761's prefill ServerArgs to contain max_running_requests=4096. Direct parsing
of the sealed task logs instead showed None in both prefill ServerArgs lines.
The later scheduler initialization logs prove 4096 for each prefill and 256 for
decode. Candidate 222763 shows 48/48/256 in ServerArgs, but no final initialized
scheduler-capacity receipt before its known graph failure.

The validator was corrected to distinguish early argument processing from
scheduler allocation. audit-capacity.py now requires both explicit arguments
and a matching final scheduler receipt for every role. Additional fixtures
reject missing final initialization and a later smaller effective ceiling.
The final validation has 4 exact-native-branch cases, 11 log-gate cases and two
historical job inspections. The failed first assertion was a diagnostic-script
assumption error, not a new GPU failure or a correction to the retained raw jobs.
No full ServerArgs pipeline or model execution was performed locally.
