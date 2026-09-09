# Cloudflare WAF Security Operations Lab

This project demonstrates an end-to-end Web Application Firewall (WAF) operations workflow using Cloudflare, Burp Suite Community Edition, and Terraform, including cross-site scripting (XSS) and SQL injection (SQLi) detection, blocking, investigation, and rule tuning.

The lab follows a small web application from onboarding through policy configuration, security testing, event investigation, false-positive tuning, rate limiting, and Infrastructure as Code (IaC) management. All security tests were authorized and performed only against the lab application.

---

## Environment

- WAF and security analytics: Cloudflare
- Test application: Python HTTP server
- Public hostname: `app.aliawaflab.com`
- Secure application publishing: Cloudflare Tunnel
- HTTP testing: Burp Suite Community Edition
- Infrastructure as Code: Terraform with the Cloudflare provider
- Development environment: Visual Studio Code on macOS

---

## Project Architecture

```text
Browser / Burp Suite
        |
        v
Cloudflare DNS, Tunnel, and WAF
        |
        v
Local Python application (127.0.0.1:8000)

Terraform ---> Cloudflare API ---> Custom WAF ruleset
```

The origin application listens only on localhost. Cloudflare Tunnel publishes it through the lab hostname so requests pass through Cloudflare's security controls before reaching the application.

---

## Project Walkthrough

### Phase 1 – Domain Setup

The `aliawaflab.com` domain was registered and activated in Cloudflare. This provided the DNS zone used for the protected application and later Terraform automation.

📸 Evidence:

- [View domain setup screenshots](Evidence/Polished/01-domain-setup)

![Cloudflare domain active](Evidence/Polished/01-domain-setup/03-cloudflare-domain-active.png)

---

### Phase 2 – Application Onboarding

A safe Python search application was created locally and validated with a benign request. Cloudflare Tunnel was then connected, and `app.aliawaflab.com` was routed to the local service at `http://127.0.0.1:8000`.

The public hostname was tested to confirm that the application was reachable through Cloudflare.

📄 Application:

- [View the Python test application](app/app.py)

📸 Evidence:

- [View application onboarding screenshots](Evidence/Polished/02-application-onboarding)

![Cloudflare protection confirmed](Evidence/Polished/02-application-onboarding/09-cloudflare-domain-protection-confirmed.png)

---

### Phase 3 – WAF Configuration

Cloudflare's security-rule interface and available managed protections were reviewed. A custom XSS rule was then configured for the lab hostname and `/search` path.

The rule initially blocked requests whose query string matched the selected XSS test pattern.

📸 Evidence:

- [View WAF configuration screenshots](Evidence/Polished/03-waf-configuration)

![Custom XSS rule active](Evidence/Polished/03-waf-configuration/16-custom-xss-rule-active-before-testing.png)

---

### Phase 4 – XSS Security Testing

A benign search was submitted first to establish expected application behavior. An authorized XSS test payload was then submitted to the same endpoint.

Cloudflare returned a block page, while the custom rule's event counter confirmed that the request had triggered the control.

📸 Evidence:

- [View security testing screenshots](Evidence/Polished/04-security-testing)

![XSS request blocked](Evidence/Polished/04-security-testing/19-xss-test-request-blocked.png)

---

### Phase 5 – Security Event Investigation

The XSS event was investigated in Cloudflare Security Analytics. The review correlated the action, rule, hostname, path, HTTP method, query string, and request metadata to confirm why the request was blocked.

The activity was identified as authorized lab testing, and no application compromise occurred.

📄 Incident report:

- [WAF Incident Investigation](docs/incident-investigation.md)

📸 Evidence:

- [View event-analysis screenshots](Evidence/Polished/05-event-analysis)

![Expanded XSS event investigation](Evidence/Polished/05-event-analysis/22-xss-event-expanded-investigation.png)

---

### Phase 6 – False-Positive Analysis and Rule Tuning

The benign search term `javascript fundamentals` was blocked because the initial XSS condition was too broad. The event was reviewed and classified as a false positive.

The rule was tuned to look for the URL-encoded `<script>` opening tag instead of the general word `script`. Validation confirmed both outcomes:

- The benign JavaScript search was allowed after tuning.
- The XSS test payload continued to be blocked.

📸 Evidence:

- [View rule-tuning screenshots](Evidence/Polished/06-rule-tuning)

![False-positive request blocked](Evidence/Polished/06-rule-tuning/24-false-positive-benign-search-blocked.png)

![Benign request allowed after tuning](Evidence/Polished/06-rule-tuning/27-benign-javascript-search-allowed-after-tuning.png)

---

### Phase 7 – SQL Injection Operations

A second custom WAF rule was configured to detect the authorized `UNION SELECT` test pattern on the `/search` endpoint.

A benign SQL-related search was allowed, while the simulated SQL injection request was blocked. The corresponding Cloudflare event was expanded and reviewed to verify the rule match and request details.

📸 Evidence:

- [View SQL injection operations screenshots](Evidence/Polished/07-sqli-operations)

![SQL injection request blocked](Evidence/Polished/07-sqli-operations/36-sqli-union-select-request-blocked.png)

![SQL injection event investigation](Evidence/Polished/07-sqli-operations/38-sqli-event-expanded-investigation.png)

---

### Phase 8 – Rate Limiting

A rate-limiting rule was configured for requests to `/search`, grouped by client IP:

- Threshold: 5 requests in 10 seconds
- Action: Block
- Mitigation duration: 10 seconds

Repeated authorized test requests exceeded the threshold. Cloudflare returned HTTP `429 Too Many Requests`, and the rate-limiting event was confirmed in Security Analytics.

📸 Evidence:

- [View rate-limiting screenshots](Evidence/Polished/08-rate-limiting)

![Rate-limit threshold triggered](Evidence/Polished/08-rate-limiting/42-rate-limit-threshold-triggered.png)

---

### Phase 9 – Burp Suite Validation and Event Correlation

Burp Suite Community Edition was used to capture application traffic and replay controlled requests with Repeater.

Testing confirmed the expected outcomes:

- Benign request: HTTP `200 OK`
- XSS test request: HTTP `403 Forbidden`
- SQL injection test request: HTTP `403 Forbidden`
- Rate-limit test: HTTP `429 Too Many Requests` after the threshold was exceeded

The Burp requests were correlated with the matching XSS, SQLi, and rate-limit events in Cloudflare.

📸 Evidence:

- [View Burp Suite screenshots](Evidence/Polished/09-burp-suite)

![Burp XSS request blocked](Evidence/Polished/09-burp-suite/48-burp-repeater-xss-request-403-response.png)

![Burp SQLi request blocked](Evidence/Polished/09-burp-suite/49-burp-repeater-sqli-request-403-response.png)

---

### Phase 10 – Terraform and Cloudflare WAF Automation

Terraform was initialized with the Cloudflare provider. The existing custom WAF ruleset was imported into Terraform state so it could be managed without recreating the live controls.

The workflow included:

1. Initializing the provider with `terraform init`.
2. Formatting and validating the configuration.
3. Running a read-only plan and refresh-only state update.
4. Importing the existing Cloudflare custom ruleset.
5. Reviewing a plan showing `0 to add, 1 to change, 0 to destroy`.
6. Applying a new `terraform-test` blocking rule.
7. Confirming the rule in Cloudflare and validating it with a blocked request and security event.

Credentials and identifiers are supplied through environment variables and are not stored in the repository. Terraform state is excluded because it may contain sensitive infrastructure data.

📄 Terraform configuration:

- [View Terraform files](terraform)

📸 Evidence:

- [View Terraform automation screenshots](Evidence/Polished/10-terraform-automation)

![Terraform apply completed](Evidence/Polished/10-terraform-automation/59-terraform-waf-rule-apply-success.png)

![Terraform-managed rule event](Evidence/Polished/10-terraform-automation/62-terraform-managed-rule-security-event.png)

---

## Security and Privacy Controls

- Testing was limited to the lab-owned hostname and application.
- User-supplied search text is HTML-escaped by the Python application.
- Cloudflare API credentials are provided through environment variables.
- API tokens, Terraform state, `.tfvars` files, and original raw evidence are excluded from Git.
- Public screenshots are sanitized to remove personal account information, local usernames, public IP addresses, and ISP information.

---

## Key Skills Demonstrated

- Cloudflare application onboarding and Tunnel configuration
- WAF policy and custom-rule implementation
- HTTP traffic and security-event analysis
- XSS and SQL injection alert investigation
- False-positive identification and rule tuning
- Rate-limit configuration and validation
- Burp Suite Proxy, HTTP history, and Repeater testing
- Security-event correlation across testing and WAF telemetry
- Terraform initialization, planning, import, and apply workflows
- Cloudflare WAF management through Infrastructure as Code
- Evidence handling, incident documentation, and credential hygiene

---

## Important Note

This repository documents a controlled educational lab. The payloads shown here were used only against infrastructure owned and authorized for this project.
