output "instance_public_ip" {
  description = "Public IP of the k3s node"
  value       = aws_instance.kubewise.public_ip
}

output "ssh_command" {
  description = "SSH into the k3s node"
  value       = "ssh ubuntu@${aws_instance.kubewise.public_ip}"
}

output "kubeconfig_command" {
  description = "Fetch kubeconfig from the node"
  value       = "ssh ubuntu@${aws_instance.kubewise.public_ip} 'sudo cat /etc/rancher/k3s/k3s.yaml'"
}
