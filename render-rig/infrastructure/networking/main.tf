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
