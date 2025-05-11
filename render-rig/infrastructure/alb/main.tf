resource "aws_lb" "render_rig2_alb" {
  name               = "render-rig2-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_sg_id]
  subnets            = [var.render_rig2_api_subnet]

  tags = {
    service = "render_rig2"
  }
}

resource "aws_lb_target_group" "render_rig2_api_tg" {
  name        = "render-rig2-api-tg"
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = {
    service = "render_rig2"
  }
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.render_rig2_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.render_rig2_api_tg.arn
  }
}
