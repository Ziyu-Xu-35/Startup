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
    total_score = item_score*0.3217+feedback_score*0.3543+seller_score*0.3240
    return total_score

def evaluation_seller(seller_cond, feedback_cond, item_cond):
    # evaluating the seller
    # response: waiting time, response rating
    # documentation: necessary: payment verification, id registration, SMS verification;
    # documentation: unnecessary: face scan, linked with social media, email verification, passport submission
    # seller: last time to activate, how long,*** how many products, and their comment( this is linked with comment
    # description change: frequency of modifying, comparative verification with tags and info
    # dilevary time condition
    selling_amount = seller_cond['selling_amount']
    time_temp = seller_cond['waiting_time']
    delivery_time = seller_cond['delivery_time']
    activate_time = seller_cond['activate_time']
    response_rating = seller_cond['response_rating']
    necessary_conditions = ['payment_verification','id_registration','SMS_verification']
    # judge whether all the conditions are 1
    face_scan = seller_cond['face_scan']
    social_media = seller_cond['social_media']
    email_verification = seller_cond['email_verification']
    passport = seller_cond['passport']
    product_number_score = seller_cond['product_number_score']
    refund_rate_score = seller_cond['refund_rate_score']
    cancellation_score = seller_cond['cancellation_score']
    visitors_profile_score = seller_cond['visitor_profile_score']
    order_time_score = seller_cond['order_time_score']
    if time_temp < 3600:
        response_time = 100
    elif 3600 <= time_temp < 18000:
        response_time = 50
    else:
        response_time = 20
    response_time_weight = response_rating_weight = 0.5
    #less connection between the two factors, so fixed weight
    face_scan_weight = social_media_weight = email_verification_weight = passport_weight = 0.25
    response_time_weight = 0.2
    response_rating_weight = 0.8
    documentation = face_scan_weight * face_scan + social_media_weight * social_media + email_verification_weight * email_verification + passport_weight * passport


    social_media_weight = 0.1
    email_verification_weight = 0.1
    face_scan_weight = 0.4
    passport_weight = 0.4

    response = response_time_weight * response_time + response_rating_weight * response_rating

    if selling_amount == 0:
        new_seller = 1
    else:
        new_seller = 0

    response_weight = 0.1081
    documentation_weight  = 0.1029+0.1200
    activate_time_weight = 0.1218
    product_number_score_weight = 0.1149
    refund_rate_score_weight = 0.1098
    cancellation_score_weight = 0.1166
    visitors_profile_score_weight = 0.1029
    order_time_score_weight = 0.1029
    if new_seller == 0:
        seller_score = response_weight*response + documentation_weight*documentation + activate_time_weight*activate_time+product_number_score_weight*product_number_score+refund_rate_score_weight*refund_rate_score+cancellation_score_weight*cancellation_score+visitors_profile_score_weight*visitors_profile_score+order_time_score_weight*order_time_score
    else: seller_score = documentation*0.9

    if all(seller_cond.get(condition, 0) == 1 for condition in necessary_conditions):
        seller_score = seller_score
    else:
        seller_score = 0
    if (response + delivery_time + activate_time)/3<0.7:
        seller_score = seller_score * 0.7
    return new_seller, seller_score

def evaluation_feedback(seller_cond, feedback_cond, item_cond):
    # buyer feedback + selling condition, after_sale condition for this product
    selling_amount = seller_cond['selling_amount']
    visiting_amount = seller_cond['visiting_amount']
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
    non_cancel_rate_weight = non_report_rate_weight = non_refund_rate_weight = selling_amount_weight = visiting_amount_weight = (18/20)/5
    comment_amount_weight = comment_verification_rating_weight = 1/20

    feedback_score = (non_refund_rate_weight*non_refund_rate+non_report_rate_weight*non_report_rate +non_cancel_rate_weight*non_cancel_rate+product_rate+comment_amount_weight*comment_amount+comment_verification_rating_weight*comment_verification_rating+selling_amount_weight*selling_amount+visiting_amount_weight*visiting_amount)

    return feedback_score, comment_keyword

def evaluation_item(seller_cond, feedback_cond, item_cond, common_price):
    # evaluate the item condition, price
    # Given weights
    weights = [0.108938547, 0.089385475, 0.082402235, 0.099162011, 0.076815642, 0.104748603, 0.089385475, 0.093575419,
               0.085195531, 0.090782123, 0.079608939]

    # Given scores
    price_score = evaluation_price(item_cond['item_price'], common_price)
    image_score = 100 * item_cond['image']
    video_score = 100 * item_cond['video']
    payment_score = 100 * item_cond['payment']
    tag_score = 100 * item_cond['tag_score']
    update_score = 100 * item_cond['update']
    refundability_score = 100 * item_cond['refundability']
    used_time_score = 100 * item_cond['used_time_score']
    tag_correspond_score = 100 * item_cond['tag_correspond']
    visiting_number_score = 100 * item_cond['visiting_number']

    # Calculate item_score
    item_score = (
            weights[0] * price_score +
            weights[1] * image_score +
            weights[2] * video_score +
            weights[3] * payment_score +
            weights[4] * tag_score +
            weights[5] * update_score +
            weights[6] * refundability_score +
            weights[7] * used_time_score +
            weights[8] * tag_correspond_score +
            weights[9] * visiting_number_score
    )

    return item_score


if __name__ == '__main__':
    print('PyCharm')
