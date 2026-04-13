def hitung_total(barang):
    total = sum(harga * jumlah for harga, jumlah in barang)
    return total


def terapkan_diskon(total, persen_diskon):
    if persen_diskon < 0 or persen_diskon > 100:
        raise ValueError("Persentase diskon harus antara 0 hingga 100")

    jumlah_diskon = (persen_diskon / 100) * total
    return total - jumlah_diskon