resource "aws_iam_role" "ec2_ssm_secrets" {
  name = "${var.project_name}-ec2-ssm-secrets-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2_ssm_secrets.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "secretsmanager" {
  role       = aws_iam_role.ec2_ssm_secrets.name
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
}

resource "aws_iam_instance_profile" "ec2_ssm_secrets" {
  name = "${var.project_name}-ec2-ssm-secrets-profile"
  role = aws_iam_role.ec2_ssm_secrets.name
}