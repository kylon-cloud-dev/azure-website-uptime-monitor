variable "yourname" {
  description = "Short lowercase name used for Azure resource naming."
  type        = string
}

variable "location" {
  description = "Azure region where resources will be deployed."
  type        = string
  default     = "East US"
}

variable "target_url" {
  description = "Website URL to monitor. Include https://."
  type        = string
}

variable "expected_text" {
  description = "Text expected to appear on the target website."
  type        = string
}

variable "alert_email" {
  description = "Email address for uptime failure alerts."
  type        = string
  sensitive   = true
}

variable "alert_phone" {
  description = "Phone number for SMS alerts in E.164 format, such as +19015551234."
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Common tags applied to supported Azure resources."
  type        = map(string)

  default = {
    project    = "website-uptime-monitor"
    managed_by = "terraform"
  }
}