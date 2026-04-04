terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    snowflake = {
      source  = "snowflakedb/snowflake"
      version = "~> 0.87.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}

provider "snowflake" {
  # Les credentials sont injectés via les variables d'environnement (SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD)
  # Pour éviter tout secret hardcodé dans le repo public.
}
