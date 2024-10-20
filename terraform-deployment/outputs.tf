output "instance_public_ip" {
  value = aws_instance.scraper_instance.public_ip
  description = "The public IP of the instance"
}
