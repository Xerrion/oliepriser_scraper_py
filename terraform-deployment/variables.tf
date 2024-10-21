variable "docker_image_name" {
  description = "Scrapes the web for the latest oil prices"
  type        = string
  default     = "xerrion/scraper-app:latest"
}

variable "base_api_url" {
  description = "The base url to scraper api"
  type = string
  default = "http://127.0.0.1"
}

variable "client_id" {
  description = "The Client ID for the scraper"
  type = string
  sensitive = true
}

variable "client_secret" {
  description = "The Client Secret for the scraper"
  type = string
  sensitive = true
}