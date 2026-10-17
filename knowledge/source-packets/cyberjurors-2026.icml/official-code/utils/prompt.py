from string import Template
import json

COMMENT_DEFAULT_ANSWER = {'Reason': '', 'Conclusion': None, }
DEFAULT_TRUSTING_SCORE = 0.5

JUDGE_DEFAULT_RESULT = {'Reason': '', 'Conclusion': None, 'reason': '', 'Buyer': None, 'Seller': None}

JUDGE_DEFAULT_RESULT_EPOCH = '{{"Reason": "", "Conclusion_{epoch}": null, "reason_{epoch}": "", "Buyer_{epoch}": null, "Seller_{epoch}": null}}'

comment_prompt_task_content_only_template = Template(
"""
你是一个专业的二手平台电商纠纷仲裁员，这是你的个人详细描述：${profile}
请根据以下信息判断买家和卖家谁更有理。
**重要注意**：请严格按照以下格式返回结果，仅返回JSON格式！
'{"Reason": "解释原因", "Conclusion": "Buyer" or "Seller"}'
"""
+
"""
【判断规则】

- 相比于商品展示图，聊天记录的商品描述、或者商品质检报告是判断商品状态的更为重要依据。
- 二手商品存在一定瑕疵属于正常现象，除商品存在重大问题，几乎全新等商品描述不构成描述不符的问题。
- 如果交易前，卖家已经展示商品信息，聊天记录中提供商品视觉信息，则证明买家下单时已经认可和了解商品及其描述，收到货后再以相关理由申请退货，非必要情况应该驳回买家退款申请。
- 买家因未仔细阅读商品展示图、聊天记录导致的事后退货诉求（无论商品描述详细与否），表示买家收到的商品与预期存在严重偏差，非必要情况应该驳回买家诉求。
- 只有买家在收到商品后，商品严重不符合卖家描述（买卖双方未事先展示过商品信息），存在严重质量问题、拍a发b、或卖家刻意隐瞒实情等类似的情况，买家证据确凿，可以退货退款。
- 仔细检查买卖双方证据和辩驳的合理性，判断买卖双方是否从视频图片中虚构了证据言论。全面考量证据，兼顾买卖双方可能的举证与过失。
- 买卖双方的纠纷讨论应该建立在卖方发货和买方收货的状态。买房应该保留拆开商品前的商品状态，拆开快递后，有严重痕迹 或 食用购买商品后的视觉证据需要审视合理性。另外，物流问题导致的发货前后状态不一致不是卖家责任。
- 仔细考虑卖家的解释逻辑，是否解决了买方的大部分困惑。判断结果只有为卖家驳回退款，或者为买家退货退款，没有其他中间折中状态。

以下是纠纷案例详情：
```
${content}
```
"""
)

comment_prompt_task_content_mf_template = Template(
"""
你是一个专业的二手平台电商纠纷仲裁员，这是你的个人详细描述：${profile}
请根据以下信息判断买家和卖家谁更有理。
**重要注意**：请严格按照以下格式返回结果，仅返回JSON格式！
'{"Reason": "解释原因", "Conclusion": "Buyer" or "Seller"}'
"""
+
"""
【判断规则】

- 相比于商品展示图，聊天记录的商品描述、或者商品质检报告是判断商品状态的更为重要依据。
- 二手商品存在一定瑕疵属于正常现象，除商品存在重大问题，几乎全新等商品描述不构成描述不符的问题。
- 如果交易前，卖家已经展示商品信息，聊天记录中提供商品视觉信息，则证明买家下单时已经认可和了解商品及其描述，收到货后再以相关理由申请退货，非必要情况应该驳回买家退款申请。
- 买家因未仔细阅读商品展示图、聊天记录导致的事后退货诉求（无论商品描述详细与否），表示买家收到的商品与预期存在严重偏差，非必要情况应该驳回买家诉求。
- 只有买家在收到商品后，商品严重不符合卖家描述（买卖双方未事先展示过商品信息），存在严重质量问题、拍a发b、或卖家刻意隐瞒实情等类似的情况，买家证据确凿，可以退货退款。
- 仔细检查买卖双方证据和辩驳的合理性，判断买卖双方是否从视频图片中虚构了证据言论。全面考量证据，兼顾买卖双方可能的举证与过失。
- 买卖双方的纠纷讨论应该建立在卖方发货和买方收货的状态。买房应该保留拆开商品前的商品状态，拆开快递后，有严重痕迹 或 食用购买商品后的视觉证据需要审视合理性。另外，物流问题导致的发货前后状态不一致不是卖家责任。
- 仔细考虑卖家的解释逻辑，是否解决了买方的大部分困惑。判断结果只有为卖家驳回退款，或者为买家退货退款，没有其他中间折中状态。

以下是纠纷案例详情：
```
${content}
```
以下是一份关于舆论的总结报告：
```
${mf_text}
```
以下是你的朋友的看法：
```
${following_comments}
```
以下是你之前的看法，你的看法可能会因为舆论而不断变化：
```
${self_comment}
```
"""
)

comment_prompt_following_comment_template = Template(
"""
{
Reason: ${Reason}
Conclusion: ${Conclusion}
}
"""
)

summary_prompt_template = Template(
"""
你在某个二手电商平台工作，职位是秘书。现在有一场交易纠纷引起了讨论，你的任务是将讨论情况总结成分析报告。
对于这场纠纷，你可能已经总结了一份包含过去评论的报告，但现在出现了一些新的评论。
你应该根据旧报告和新评论写一份新报告。
您的报告必须包括：
1.评论者提及的观点;
2.是否存在激烈的辩论;
3.当前舆论倾向于支持谁。

以下是纠纷案例详情
```
${content}
```

以下是讨论情况
```
${comment}
```

以下是旧报告：
```
${mf_text}
```
"""
)

summary_prompt_comment_template = Template(
'''
{
支持对象：${verdict}
原因： ${reasoning}
}
'''
)

judge_prompt_task_template = Template(
"""
你是一个专业的二手平台电商纠纷仲裁员。
请根据以下信息判断买家和卖家谁更有理，为每一方的诉求和证据确凿程度打分。两个分数必须加起来正好等于17，分数越大表示越支持哪方。
**重要注意**：请严格按照以下格式返回结果，仅返回JSON格式！
'{"Reason": "解释原因", "Conclusion": "Buyer" or "Seller", "Buyer": X, "Seller": Y}'
"""
+
"""
【判断规则】

- 相比于商品展示图，聊天记录的商品描述、或者商品质检报告是判断商品状态的更为重要依据。
- 二手商品存在一定瑕疵属于正常现象，除商品存在重大问题，几乎全新等商品描述不构成描述不符的问题。
- 如果交易前，卖家已经展示商品信息，聊天记录中提供商品视觉信息，则证明买家下单时已经认可和了解商品及其描述，收到货后再以相关理由申请退货，非必要情况应该驳回买家退款申请。
- 买家因未仔细阅读商品展示图、聊天记录导致的事后退货诉求（无论商品描述详细与否），表示买家收到的商品与预期存在严重偏差，非必要情况应该驳回买家诉求。
- 只有买家在收到商品后，商品严重不符合卖家描述（买卖双方未事先展示过商品信息），存在严重质量问题、拍a发b、或卖家刻意隐瞒实情等类似的情况，买家证据确凿，可以退货退款。
- 仔细检查买卖双方证据和辩驳的合理性，判断买卖双方是否从视频图片中虚构了证据言论。全面考量证据，兼顾买卖双方可能的举证与过失。
- 买卖双方的纠纷讨论应该建立在卖方发货和买方收货的状态。买房应该保留拆开商品前的商品状态，拆开快递后，有严重痕迹 或 食用购买商品后的视觉证据需要审视合理性。另外，物流问题导致的发货前后状态不一致不是卖家责任。
- 仔细考虑卖家的解释逻辑，是否解决了买方的大部分困惑。判断结果只有为卖家驳回退款，或者为买家退货退款，没有其他中间折中状态。

以下是纠纷案例详情：
```
${content}
```
以下是非专业人士的看法：
```
${comment}
```
"""
)

judge_prompt_task_mf_template = Template(
"""
你是一个专业的二手平台电商纠纷仲裁员。
请根据以下信息判断买家和卖家谁更有理，为每一方的诉求和证据确凿程度打分。两个分数必须加起来正好等于17，分数越大表示越支持哪方。
**重要注意**：请严格按照以下格式返回结果，仅返回JSON格式！
'{"Reason": "解释原因", "Conclusion": "Buyer" or "Seller", "Buyer": X, "Seller": Y}'
"""
+
"""
【判断规则】

- 相比于商品展示图，聊天记录的商品描述、或者商品质检报告是判断商品状态的更为重要依据。
- 二手商品存在一定瑕疵属于正常现象，除商品存在重大问题，几乎全新等商品描述不构成描述不符的问题。
- 如果交易前，卖家已经展示商品信息，聊天记录中提供商品视觉信息，则证明买家下单时已经认可和了解商品及其描述，收到货后再以相关理由申请退货，非必要情况应该驳回买家退款申请。
- 买家因未仔细阅读商品展示图、聊天记录导致的事后退货诉求（无论商品描述详细与否），表示买家收到的商品与预期存在严重偏差，非必要情况应该驳回买家诉求。
- 只有买家在收到商品后，商品严重不符合卖家描述（买卖双方未事先展示过商品信息），存在严重质量问题、拍a发b、或卖家刻意隐瞒实情等类似的情况，买家证据确凿，可以退货退款。
- 仔细检查买卖双方证据和辩驳的合理性，判断买卖双方是否从视频图片中虚构了证据言论。全面考量证据，兼顾买卖双方可能的举证与过失。
- 买卖双方的纠纷讨论应该建立在卖方发货和买方收货的状态。买房应该保留拆开商品前的商品状态，拆开快递后，有严重痕迹 或 食用购买商品后的视觉证据需要审视合理性。另外，物流问题导致的发货前后状态不一致不是卖家责任。
- 仔细考虑卖家的解释逻辑，是否解决了买方的大部分困惑。判断结果只有为卖家驳回退款，或者为买家退货退款，没有其他中间折中状态。

以下是纠纷案例详情：
```
${content}
```
以下是非专业人士的看法：
```
${comment}
```
以下是一份关于舆论的总结报告：
```
${mf_text}
```
"""
)

judge_prompt_comment_template = summary_prompt_comment_template

def get_case_info_text(item):
    prompt_text = f"商品类型： {{{item['product']}}}\n"
    prompt_text += f"买家申诉：{{{item['buyer_claim']}}}\n"
    prompt_text += f"卖家申诉：{{{item['seller_claim']}}}\n"
    image_index = 0
    video_index = 0
    prompt_text += "以下是买方提供的理由：\n"
    for evidence in item['buyer_evidence']:
        prompt_text += evidence['text']
        evidence['image_paths'] = evidence['image_paths'] or []
        for _ in evidence['image_paths']:
            image_index += 1
            prompt_text += f"<图片{image_index}>"
        evidence['video_paths'] = evidence['video_paths'] or []
        for _ in evidence['video_paths']:
            video_index += 1
            prompt_text += f"<视频{video_index}>"
            
    prompt_text += "以下是卖方提供的理由：\n"
    for evidence in item['seller_evidence']:
        prompt_text += evidence['text']
        evidence['image_paths'] = evidence['image_paths'] or []
        for _ in evidence['image_paths']:
            image_index += 1
            prompt_text += f"<图片{image_index}>"
        evidence['video_paths'] = evidence['video_paths'] or []
        for _ in evidence['video_paths']:
            video_index += 1
            prompt_text += f"<视频{video_index}>"
    return prompt_text

if __name__ == "__main__":
    result = json.loads(JUDGE_DEFAULT_RESULT_EPOCH.format(epoch=5))
    if result['Conclusion_5'] is None:
        print(result)