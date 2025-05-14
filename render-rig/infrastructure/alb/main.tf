resource "aws_lb" "render-rig2-alb" {
  name               = "render-rig2-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_sg_id]
  subnets            = [var.render_rig2_api_subnet_id, var.render_rig2_worker_subnet_id]

  tags = {
    service = "render_rig2"
  }
}

resource "aws_lb_target_group" "render-rig2-api-tg" {
  name        = "render-rig2-api-tg"
  port        = 8000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 45
    timeout             = 30
    healthy_threshold   = 2
    unhealthy_threshold = 5
  }

  tags = {
    service = "render_rig2"
  }
}

// This block defines an HTTP listener for the ALB. 
// It listens on port 80 and forwards incoming traffic to the specified target group.
resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.render-rig2-alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.render-rig2-api-tg.arn
  }
}
