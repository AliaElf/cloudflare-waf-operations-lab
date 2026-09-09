output "custom_waf_ruleset_id" {
  description = "ID of the existing zone custom WAF ruleset"

  value = one([
    for ruleset in data.cloudflare_rulesets.zone.rulesets :
    ruleset.id
    if ruleset.phase == "http_request_firewall_custom" && ruleset.kind == "zone"
  ])

  sensitive = true
}