resource "yandex_compute_disk" "udp-joker-disk" {
  name     = "udp-joker-disk"
  type     = "network-hdd"
  zone     = "ru-central1-b"
  size     = "10"
  image_id = "fd837neerofcjnk6sksg"
}

resource "yandex_compute_instance" "upd-joker-vm" {
  name = "upd-joker"

  platform_id = "standard-v3"

  resources {
    cores         = 2
    memory        = 1
    core_fraction = 25
  }

  boot_disk {
    disk_id = yandex_compute_disk.udp-joker-disk.id
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.udp-joker-subnet.id
    nat       = true
  }

  metadata = {
    ssh-keys = "udp-joker:${file("~/.ssh/id_ed25519.pub")}"
  }
}


resource "yandex_vpc_network" "udp-joker-network" {
  name = "udp-joker-network"
}

resource "yandex_vpc_subnet" "udp-joker-subnet" {
  name           = "udp-joker-subnet"
  zone           = "ru-central1-b"
  network_id     = yandex_vpc_network.udp-joker-network.id
  v4_cidr_blocks = ["192.168.10.0/24"]
}

output "internal_ip_address_vm_1" {
  value = yandex_compute_instance.upd-joker-vm.network_interface.0.ip_address
}

output "external_ip_address_vm_1" {
  value = yandex_compute_instance.upd-joker-vm.network_interface.0.nat_ip_address
}
