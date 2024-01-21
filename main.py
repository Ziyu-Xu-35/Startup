import numpy as np
from scipy import stats

# limited: secondhand, p2p
# one comment for one product
# overall factor: new seller or not
# rules: all functions input and output is 0-100, evaluation_interaction is the main function
# rules: other evaluation functions are evaluating different parts, and interaction means the overall interface and output
# Use the Box-Cox transformation to make the data follow a normal distribution
def transform_to_normal_distribution(data):
    transformed_data, lmbda = stats.boxcox(data)
    mean = np.mean(transformed_data)
    std = np.std(transformed_data)
    return transformed_data, mean, std

 # Transform the common_price array to follow a normal distribution
def evaluation_price(item_price, common_price):
    common_price_transformed, common_price_mean, common_price_std = transform_to_normal_distribution(common_price)
    item_price_transformed = (item_price - common_price_mean) / common_price_std
    temp = abs(item_price_transformed)
    # Use the same transformation parameters to transform item_price
    if temp <= common_price_std:
        price_eva = 100
    elif temp < 2 * common_price_std or temp > common_price_std:
        price_eva = 80
    elif temp < 3 * common_price_std or temp > 2 * common_price_std:
        price_eva = 30
    else:
        price_eva = 0

    return price_eva


def evaluation(seller_cond, feedback_cond, item_cond):
    seller_score = evaluation_seller(seller_cond, feedback_cond, item_cond)
    feedback_score = evaluation_feedback(seller_cond, feedback_cond, item_cond)
    item_score = evaluation_item(seller_cond, feedback_cond, item_cond)
    total_score = (seller_score + feedback_score + item_score)/3
    return total_score

def evaluation_seller(seller_cond, feedback_cond, item_cond):
    # evaluating the seller
    # response: waiting time, response rating
    # documentation: necessary: payment verification, id registration, SMS verification;
    # documentation: unnecessary: face scan, linked with social media, email verification, passport submission
    # seller: last time to activate, how long,*** how many products, and their comment( this is linked with comment
    # description change: frequency of modifying, comparative verification with tags and info
    # delivary time condition
    selling_amount = seller_cond['selling_amount']
    visiting_amount = seller_cond['visiting_amount']
    time_temp = seller_cond['waiting_time']
    delivery_time = seller_cond['delivery_time']
    activate_time = seller_cond['activate_time']
    response_rating = seller_cond['response_rating']
    if time_temp < 3600:
        response_time = 100
    elif 3600 <= time_temp < 18000:
        response_time = 50
    else:
        response_time = 20
    response_time_weight = response_rating_weight = 0.5
    response = response_time_weight*response_time + response_rating_weight * response_rating
    
    necessary_conditions = ['payment_verification','id_registration','SMS_verification']
    # judge whether all the conditions are 1
    face_scan = seller_cond['face_scan']
    social_media = seller_cond['social_media']
    email_verification = seller_cond['email_verification']
    passport = seller_cond['passport']
    face_scan_weight = social_media_weight = email_verification_weight = passport_weight = 0.25
    documentation = face_scan_weight*face_scan + social_media_weight*social_media+email_verification_weight*email_verification+passport_weight*passport

    if selling_amount == 0:
        new_seller = 1
    else:
        new_seller = 0

    if new_seller == 0:
        seller_score = response + documentation + delivery_time + activate_time
    else: seller_score = documentation

    if all(seller_cond.get(condition, 0) == 1 for condition in necessary_conditions):
        seller_score = seller_score
    else:
        seller_score = 0
    return new_seller, seller_score

def evaluation_feedback(seller_cond, feedback_cond, item_cond):
    # buyer feedback + selling condition, after_sale condition for this product
    product_rate = feedback_cond['seller_product_rate']
    non_refund_rate = seller_cond['non_refund_rate']
    non_report_rate = seller_cond['non_report_rate']
    non_cancel_rate = seller_cond['non_cancel_rate']
    # rating is an array
    comment_verification_rating = feedback_cond['rating']
    # this is an array dictionary, like comment_verification_rating[i]['rating'], ['verification']: 1 or 0
    # keyword is also a char array, maybe 5 keywords which appear most frequently
    comment_keyword = feedback_cond['comment_keyword']
    comment_amount = feedback_cond['comment_amount']
    non_cancel_rate_weight = non_report_rate_weight = non_refund_rate_weight = comment_amount_weight = comment_verification_rating_weight = 0.2
    
    feedback_score = (non_refund_rate_weight*non_refund_rate+non_report_rate_weight*non_report_rate +non_cancel_rate_weight*non_cancel_rate+product_rate+comment_amount_weight*comment_amount+comment_verification_rating_weight*comment_verification_rating)

    return feedback_score, comment_keyword

def evaluation_item(seller_cond, feedback_cond, item_cond, common_price):
    # evaluate the item condition, price
    price_eva = evaluation_price(item_cond['item_price'], common_price)
    product_eva = 20 * item_cond['product_condition']
    item_score = (price_eva + product_eva - price_eva)
    return item_score
    #product_condition is to describe how new the product is, chosen from 5 stages

if __name__ == '__main__':
    print('PyCharm')
