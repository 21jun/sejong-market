from monthly.database.database import DataBase

class RecommendInstallment:
    def __init__(self, user_id):
        self.db = DataBase()
        self.user_id = user_id
        
    def get_product_installment(self, x):
        SQL = "select *, if (intr_rate_type_nm = '단리', ({x}*save_trm + ({x}*save_trm*(intr_rate2/100)*(save_trm/12))), (({x}*save_trm) * POW((1 + (intr_rate2/100)), (save_trm/12))))  from prod_recommend_installment join v_product_installment USING(matching_id) where user_id = {user_id} order by intr_rate2 DESC;"
        self.db.cur.execute(SQL.format(user_id=self.user_id, x=x))
        data = self.db.cur.fetchall()

        product_dict_list=[]
        for installment in data:
            product_dict={}
            product_dict['matching_id']         = installment[0] if installment[0] is not None else ""
            product_dict['user_id']             = installment[2] if installment[2] is not None else 0
            product_dict['name']                = installment[4] if installment[4] is not None else "" 
            product_dict['organization_code']   = installment[5] if installment[5] is not None else ""
            product_dict['organization_diplay'] = installment[6] if installment[6] is not None else ""
            product_dict['mtrt_int']            = installment[7] if installment[7] is not None else ""
            product_dict['spcl_cnd']            = installment[8] if installment[8] is not None else ""
            product_dict['etc_note']            = installment[9] if installment[9] is not None else ""
            product_dict['dcls_strt_day']       = installment[10] if installment[10] is not None else ""
            product_dict['dcls_end_day']        = installment[11] if installment[11] is not None else ""
            product_dict['intr_rate_type_nm']   = installment[12] if installment[12] is not None else ""
            product_dict['rsrv_type_nm']        = installment[13] if installment[13] is not None else ""
            product_dict['max_limit']           = installment[14] if installment[14] is not None else 0
            product_dict['save_trm']            = installment[15] if installment[15] is not None else 0
            product_dict['intr_rate']           = installment[16] if installment[16] is not None else 0
            product_dict['intr_rate2']          = installment[17] if installment[17] is not None else 0
            product_dict['join_way']            = installment[18] if installment[18] is not None else ""
            product_dict['join_member']         = installment[19] if installment[19] is not None else ""
            product_dict['join_job']            = installment[20] if installment[20] is not None else ""
            product_dict['join_age_min']        = installment[21] if installment[21] is not None else 0
            product_dict['join_age_max']        = installment[22] if installment[22] is not None else 0
            product_dict['join_regio']          = installment[23] if installment[23] is not None else ""
            product_dict['benefit']             = installment[24] if installment[24] is not None else 0.0
            product_dict['x']                   = x
            product_dict_list.append(product_dict)
    
        return product_dict_list
    
    def get_recommned_message(self, x):
        SQL = "SELECT name from user where user_id ={user_id}"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()
        name = data[0][0]

        if self.user_id == 101:
            message = f"{name}님, 월마다 남는 약 {x}원을 아래 적금 상품들로 관리해보세요 😉"
        elif self.user_id == 105:
            message = f"{name}님, 현재 사용중인 적금 상품보다 좋은 조건의 상품들이 있어요. 😉"
        elif self.user_id == 106:
            message = f"{name}님, 월마다 남는 약 {x}원을 아래 적금 상품들로 관리해보세요. 😉 "
        else:
            message = f"{name}님, 금리가 높은 적금 상품들을 추천해드릴게요😉"

        return message
    
class RecommendSaving:
    def __init__(self, user_id):
        self.db = DataBase()
        self.user_id = user_id
        
    def get_product_saving(self, x):
        SQL = "select *,if (intr_rate_type_nm = '단리', ({x} + ({x}*(intr_rate2/100)*(save_trm/12))), ({x} * POW((1 + (intr_rate2/100)), (save_trm/12)))) from prod_recommend_saving join v_product_saving USING(matching_id) where user_id = {user_id} order by intr_rate2 DESC;"
        self.db.cur.execute(SQL.format(user_id=self.user_id, x = x))
        data = self.db.cur.fetchall()

        """
        matching_id	                0
        prod_id	
        user_id	
        prod_id	
        name
        organization_code	        5
        organization_diplay	
        mtrt_int	
        spcl_cnd	
        etc_note	
        dcls_strt_day	            10
        dcls_end_day	
        intr_rate_type_nm	
        max_limit	
        save_trm	
        intr_rate	                15
        intr_rate2	
        join_way	
        join_member	
        join_job	
        join_age_min	            20
        join_age_max	
        join_region
        """
        product_dict_list=[]
        for installment in data:
            product_dict={}
            product_dict['matching_id']         = installment[0] if installment[0] is not None else ""
            product_dict['user_id']             = installment[2] if installment[2] is not None else 0
            product_dict['name']                = installment[4] if installment[4] is not None else "" 
            product_dict['organization_code']   = installment[5] if installment[5] is not None else ""
            product_dict['organization_diplay'] = installment[6] if installment[6] is not None else ""
            product_dict['mtrt_int']            = installment[7] if installment[7] is not None else ""
            product_dict['spcl_cnd']            = installment[8] if installment[8] is not None else ""
            product_dict['etc_note']            = installment[9] if installment[9] is not None else ""
            product_dict['dcls_strt_day']       = installment[10] if installment[10] is not None else ""
            product_dict['dcls_end_day']        = installment[11] if installment[11] is not None else ""
            product_dict['intr_rate_type_nm']   = installment[12] if installment[12] is not None else ""
            product_dict['max_limit']           = installment[13] if installment[13] is not None else 0
            product_dict['save_trm']            = installment[14] if installment[14] is not None else 0
            product_dict['intr_rate']           = installment[15] if installment[15] is not None else 0
            product_dict['intr_rate2']          = installment[16] if installment[16] is not None else 0
            product_dict['join_way']            = installment[17] if installment[17] is not None else ""
            product_dict['join_member']         = installment[18] if installment[18] is not None else ""
            product_dict['benefit']             = installment[19] if installment[19] is not None else 0.0
            product_dict['x']                   = x
            product_dict_list.append(product_dict)

        print(product_dict_list)
        return product_dict_list
    
    def get_recommned_message(self, x):
        SQL = "SELECT name from user where user_id ={user_id}"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()
        name = data[0][0]
        
        if self.user_id == 102:
            message = f"통장에 숨은 {x}원의 여유자금, 아래 예금 상품으로 관리하세요. 🤗"
        else:
            message = f"{name}님, 금리가 높은 예금 상품들을 추천해드릴게요🤗"
        
        return message


class RecommendLoan:
    def __init__(self, user_id):
        self.db = DataBase()
        self.user_id = user_id
        
    def get_product_loan(self):
        SQL = "select * from prod_recommend_loan join v_product_loan USING(matching_id) where user_id = {user_id};"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()

        """
        matching_id	            0
        prod_id	                
        user_id	
        prod_id
        name	
        organization_diplay	    5
        crdt_prdt_type_nm	
        join_way	
        crdt_lend_rate_type_nm	
        crdt_grad_1	
        crdt_grad_4	            10
        crdt_grad_5	
        crdt_grad_6	
        crdt_grad_10	
        crdt_grad_avg           14
        """
        product_dict_list=[]
        for loan in data:
            product_dict={}
            product_dict['matching_id']                         = loan[0] if loan[0] is not None else ""
            product_dict['user_id']                             = loan[2] if loan[2] is not None else 0
            product_dict['name']                                = loan[4] if loan[4] is not None else ""
            product_dict['organization_diplay']                 = loan[5] if loan[5] is not None else ""
            product_dict['organization_code']                   = ""
            product_dict['crdt_prdt_type_nm']                   = loan[6] if loan[6] is not None else ""
            product_dict['join_way']                            = loan[7] if loan[7] is not None else ""
            product_dict['crdt_lend_rate_type_nm']              = loan[8] if loan[8] is not None else ""
            product_dict['crdt_grad_1']                         = loan[9] if loan[9] is not None else 0
            product_dict['crdt_grad_4']                         = loan[10] if loan[10] is not None else 0
            product_dict['crdt_grad_5']                         = loan[11] if loan[11] is not None else 0
            product_dict['crdt_grad_6']                         = loan[12] if loan[12] is not None else 0
            product_dict['crdt_grad_10']                        = loan[13] if loan[13] is not None else ""
            product_dict['crdt_grad_avg']                       = loan[14] if loan[14] is not None else ""
            product_dict_list.append(product_dict)
    
        return product_dict_list
    
    def get_recommned_message(self):
        SQL = "SELECT name, credit from user where user_id ={user_id}"
        self.db.cur.execute(SQL.format(user_id=self.user_id))
        data = self.db.cur.fetchall()
        name = data[0][0]
        credit = data[0][1] if data[0][1] is not None else 0
        x = 1000000

        if self.user_id == 103:
            x = 52800
            message = f"{name}님, ({credit} 등급) 아래 대출 상품을 이용하시면\n 이자를 월 최대 {x}원 절약하실 수 있어요. 😘"
        elif self.user_id == 104:
            x = 28490
            message = f"{name}님, ({credit} 등급) 아래 대출 상품을 이용하시면\n 이자를 월 최대 {x}원 절약하실 수 있어요. 😘"
        else:
            message = f"{name}님, ({credit} 등급) 현재 사용중인 대출 상품보다 좋은 조건의 상품들이 있어요. 😘"

        return message