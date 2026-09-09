# WAF Incident Investigation

## Incident Summary

| Field | Details |
| --- | --- |
| Incident ID | WAF-IR-001 |
| Environment | `app.aliawaflab.com` lab application |
| Detection source | Cloudflare Security Analytics |
| Activity | XSS, SQL injection, and high-rate request simulations |
| Status | Closed – Authorized testing |
| Severity | Informational in the controlled lab environment |
| Impact | No compromise or data loss observed |

This report documents the investigation of WAF events generated during authorized testing of the lab-owned application. The goal was to practice the same operational sequence used when triaging web-security alerts: validate the detection, inspect request context, distinguish malicious patterns from false positives, tune controls, retest, and document the result.

---

## Systems and Data Sources

- Cloudflare custom WAF rules
- Cloudflare rate-limiting rules
- Cloudflare Security Analytics and sampled event logs
- Burp Suite Community Edition Proxy and Repeater
- Local Python application logs
- Terraform-managed Cloudflare WAF configuration

---

## Detection Overview

### XSS test event

- Rule: `Block XSS Test Pattern - Search Query`
- Host: `app.aliawaflab.com`
- Path: `/search`
- Method: `GET`
- Test pattern: URL-encoded `<script>` opening tag
- Cloudflare action: `Block`
- Client result: HTTP `403 Forbidden`

### SQL injection test event

- Rule: `Block SQLi UNION SELECT - Search Query`
- Host: `app.aliawaflab.com`
- Path: `/search`
- Method: `GET`
- Test pattern: `UNION SELECT`
- Cloudflare action: `Block`
- Client result: HTTP `403 Forbidden`

### Rate-limit event

- Rule: `Rate Limit Search Requests Per IP`
- Scope: requests to `/search`
- Threshold: 5 requests in 10 seconds per client IP
- Mitigation duration: 10 seconds
- Cloudflare action: `Block`
- Client result after threshold: HTTP `429 Too Many Requests`

---

## Investigation Process

### 1. Establish a baseline

Benign requests were sent to the search endpoint before and after security controls were deployed. The application returned HTTP `200`, confirming that normal traffic could reach the origin.

### 2. Reproduce the detections

Controlled XSS and SQL injection patterns were submitted through the application and replayed with Burp Suite Repeater. Cloudflare returned HTTP `403` for both malicious-pattern tests.

Repeated benign requests were then sent within the rate-limit window. The request exceeding the configured threshold received HTTP `429`.

### 3. Review Cloudflare event context

Each event was reviewed for:

- Action taken
- Matching rule and service
- Request timestamp
- Hostname and path
- HTTP method and version
- Query-string pattern
- Client and user-agent context
- Cloudflare request and ruleset identifiers

The reviewed fields matched the authorized tests and confirmed that the expected control generated each event.

### 4. Correlate client and WAF evidence

Burp Suite response codes and request payloads were compared with the corresponding Cloudflare events:

| Test | Burp/client result | Cloudflare result | Assessment |
| --- | --- | --- | --- |
| Benign search | `200 OK` | Allowed | Expected behavior |
| XSS pattern | `403 Forbidden` | Custom-rule block | True positive test |
| SQLi pattern | `403 Forbidden` | Custom-rule block | True positive test |
| Request burst | `429 Too Many Requests` | Rate-limit block | Threshold enforced |

---

## False-Positive Analysis and Tuning

The initial XSS condition also blocked the benign phrase `javascript fundamentals`. The word `javascript` contains `script`, so the broad query match treated legitimate traffic as suspicious.

### Root cause

The initial detection logic matched a generic substring instead of a sufficiently specific attack pattern.

### Remediation

The rule was narrowed to match the URL-encoded `<script>` opening tag (`%3Cscript%3E`) on the designated hostname and `/search` path.

### Validation

- `javascript fundamentals` was allowed after tuning.
- The encoded XSS test payload remained blocked.
- Cloudflare continued to record the malicious-pattern event.

This change improved rule precision while preserving the intended protection.

---

## Terraform Change Validation

The existing Cloudflare custom ruleset was brought under Terraform management. A new rule matching the controlled `terraform-test` query pattern was added through Infrastructure as Code.

Before applying the change, the Terraform plan showed:

```text
Plan: 0 to add, 1 to change, 0 to destroy.
```

After approval, the apply completed successfully with one ruleset change. The rule was visible as active in Cloudflare, a matching request was blocked, and the corresponding event was confirmed in Security Analytics.

---

## Impact Assessment

- No unauthorized party was identified.
- No backend database or production data was present in the test application.
- The Python application HTML-escaped reflected search input.
- Blocked requests did not demonstrate origin compromise.
- All observed activity was generated intentionally as part of the lab.

---

## Disposition

The events were classified as authorized security-control validation. The XSS false positive was remediated through rule tuning, and all controls were retested successfully.

**Final status:** Closed – Authorized testing; controls operating as expected.

---

## Evidence

- [XSS event analysis](../Evidence/Polished/05-event-analysis)
- [XSS false-positive tuning](../Evidence/Polished/06-rule-tuning)
- [SQL injection operations](../Evidence/Polished/07-sqli-operations)
- [Rate-limit investigation](../Evidence/Polished/08-rate-limiting)
- [Burp Suite correlation](../Evidence/Polished/09-burp-suite)
- [Terraform-managed WAF validation](../Evidence/Polished/10-terraform-automation)

Sensitive values, including the testing source IP and local account information, were removed from the public evidence copies.

---

## Lessons Learned

- Detection quality requires both true-positive and benign validation.
- Broad substring matching can create avoidable false positives.
- HTTP response codes provide useful client-side evidence but should be correlated with WAF telemetry.
- Rate limiting addresses abusive request volume rather than payload content.
- Terraform plans should be reviewed before applying WAF changes.
- WAF event exports and Terraform state require careful handling because they may contain sensitive operational data.
