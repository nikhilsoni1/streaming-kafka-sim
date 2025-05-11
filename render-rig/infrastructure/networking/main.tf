resource "aws_subnet" "render_rig2_api_subnet" {
  vpc_id                  = var.vpc_id
  cidr_block              = var.cidr_block[0]
  availability_zone       = var.availability_zones[0]
  map_public_ip_on_launch = true

  tags = {
    Name    = "subnet_render_rig2_api"
    service = "render_rig2"
  }
}

resource "aws_subnet" "render_rig2_worker_subnet" {
  vpc_id            = var.vpc_id
  cidr_block        = var.cidr_block[1]
  availability_zone = var.availability_zones[1]

  tags = {
    Name    = "subnet_render_rig2_worker"
    service = "render_rig2"
  }
}

resource "aws_route_table" "public" {
  vpc_id = var.vpc_id

  tags = {
    Name    = "render_rig2_public_rt"
    service = "render_rig2"
  }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.render_rig2_api_subnet.id
  route_table_id = aws_route_table.public.id
}

resource "aws_internet_gateway" "render_rig2_igw" {
  vpc_id = var.vpc_id

  tags = {
    Name    = "render_rig2_igw"
    service = "render_rig2"
  }

}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.render_rig2_igw.id
}

# ALB
resource "aws_security_group" "render_rig2_alb_sg" {
  name        = "render_rig2_alb_sg"
  description = "Allow HTTP from anywhere to ALB"
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow HTTP from the internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "render_rig2_alb_sg"
    service = "render_rig2"
  }
}
