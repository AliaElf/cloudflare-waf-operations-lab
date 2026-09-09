data "cloudflare_rulesets" "zone" {
  zone_id = var.cloudflare_zone_id
}