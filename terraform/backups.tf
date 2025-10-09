resource "yandex_backup_policy" "udp-joker-backup-policy" {
  name = "udp-joker-weekly-backup"

  scheduling {
    enabled = true
    scheme  = "ALWAYS_INCREMENTAL"
    weekly_backup_day = "MONDAY" 
    
    backup_sets {
      execute_by_time {
        type      = "WEEKLY"
        weekdays  = ["MONDAY"] 
        repeat_at = ["02:00"] 
      }
      type = "TYPE_AUTO"
    }
  }

  retention {
    after_backup = true
    
    rules {
      max_count = 2 
      repeat_period = ["WEEKLY"]
    }
  }

  reattempts {
    enabled      = true
    interval     = "5m"
    max_attempts = 3
  }

  vm_snapshot_reattempts {
    enabled      = true
    interval     = "5m"
    max_attempts = 3
  }

  fast_backup_enabled               = true
  multi_volume_snapshotting_enabled = true
  compression                       = "NORMAL"
  cbt                               = "USE_IF_ENABLED"
}

resource "yandex_backup_policy_bindings" "udp-joker-backup-binding" {
  instance_id = yandex_compute_instance.upd-joker-vm.id
  policy_id   = yandex_backup_policy.udp-joker-backup-policy.id
}