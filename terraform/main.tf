resource "cloudflare_ruleset" "custom_waf" {
  zone_id = var.cloudflare_zone_id
  name    = "default"
  kind    = "zone"
  phase   = "http_request_firewall_custom"

  rules = [
    {
      ref         = "540d6745cb074949a033b12a7efd1c0f"
      description = "Block XSS Test Pattern - Search Query"
      expression  = "(http.host eq \"app.aliawaflab.com\" and http.request.uri.path eq \"/search\" and http.request.uri.query contains \"%3Cscript%3E\")"
      action      = "block"
      enabled     = true
    },
    {
      ref         = "60b0cfc98ecb4123ab8962783188ad21"
      description = "Block SQLi UNION SELECT - Search Query"
      expression  = "(http.host eq \"app.aliawaflab.com\" and http.request.uri.path eq \"/search\" and http.request.uri.query contains \"UNION+SELECT\")"
      action      = "block"
      enabled     = true
    },
    {
      ref         = "terraform_block_test_pattern"
      description = "Block Terraform Test Pattern - Search Query"
      expression  = "(http.host eq \"app.aliawaflab.com\" and http.request.uri.path eq \"/search\" and http.request.uri.query contains \"terraform-test\")"
      action      = "block"
      enabled     = true
    },
  ]
}
