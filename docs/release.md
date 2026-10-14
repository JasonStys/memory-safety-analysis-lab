# Source-release and maintenance checklist

Author: Jason Stys. This is a portfolio source release, not a production service or installer deployment.

Before handoff, verify exact final-main SHA and every matrix, sanitizer/fuzz, benchmark, security and CodeQL job. Verify the complete tracked inventory, ignore rules, code-map/file-guide drift, private-state exclusion and default-build isolation. Record real expected/observed diagnostic assertions, scoped coverage and immutable source/run links in the validation report. Do not infer final-main success from the prior commit's badge.

Compile only authored safe sources in default builds. Reproduce a failure with a synthetic input and stable error code. Preserve original input and incomplete review separately, rebuild a known passing source in a separate checkout, and retest all supported platforms. Never reset user changes or suppress a repaired-code alert/test to obtain green output. No migration, hosted account, on-call notification, driver, Docker change or signed binary release is part of this handoff.

Future Actions checks must include current artifact/cache bytes and available account meter, with billing evidence kept local. CodeQL's internal extraction and dependency caches are explicitly disabled as well as database/artifact uploads. Existing verification caches are retained until Jason approves an exact cleanup scope; no prior approval is reused and no billing/retention setting is changed.
