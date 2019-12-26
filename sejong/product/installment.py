from monthly.database.database import DataBase


class ProductInstallment:
    def __init__(self):
        self.db = DataBase()

    def get_product_installment(self):
        SQL = "SELECT * FROM v_product_installment;"
        self.db.cur.execute(SQL)
        data = self.db.cur.fetchall()

        installment_list = []
        for installment in data:
            installment_dict = {}
            installment_dict['fin_prdt_cd'] = installment[0]
            installment_dict['dcls_month'] = installment[2]
            installment_dict['kor_co_nm'] = installment[4]
            installment_dict['fin_prdt_nm'] = installment[5]
            installment_dict['join_way'] = installment[6]
            installment_dict['mtrt_int'] = installment[7]
            installment_dict['spcl_cnd'] = installment[8]
            installment_dict['join_member'] = installment[10]
            installment_dict['etc_note'] = installment[11]
            installment_dict['max_limit'] = installment[12]
            installment_dict['intr_rate_type_nm'] = installment[19]
            installment_dict['rsrv_type_nm'] = installment[21]
            installment_dict['intr_rate'] = installment[23]
            installment_dict['intr_rate2'] = installment[24]
 
            installment_list.append(installment_dict)

        return installment_list