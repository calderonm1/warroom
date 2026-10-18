# infra/: Terraform for AWS

Not yet scaffolded. Created by epic `EP-03`. See [infrastructure (AWS)](../docs/03-architecture/infrastructure-aws.md), [ADR-0007](../docs/adr/0007-cloud-aws.md) and [ADR-0008](../docs/adr/0008-iac-terraform.md).

```
infra/
  bootstrap/              one-time: state bucket, GitHub OIDC provider, deploy roles (per account)
  org/                    AWS Organizations, accounts, SCPs, IAM Identity Center, budgets
  modules/
    network/  ecs-service/  aurora/  valkey/  cdn/  cognito/  observability/  agent-access/
  envs/
    dev/      <stack>/main.tf
    staging/  <stack>/main.tf
    prod/     <stack>/main.tf
```

Agents may `plan` anywhere and `apply` in `dev` only (see [`ops/environments/`](../ops/environments/)).
