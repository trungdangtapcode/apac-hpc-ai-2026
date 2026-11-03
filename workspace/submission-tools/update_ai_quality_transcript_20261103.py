#!/usr/bin/env python3
"""Apply the reviewed 3 November local quality result to AI transcript rows."""

import json
from pathlib import Path


TRANSCRIPT = Path(
    "/home/apacsc42/workspace/reports/ai-final-report-20261030/"
    "investigation-transcript.json"
)

SLIDE_16 = {
    "title": "The optimised service retains 99.9154% of reference accuracy",
    "en": {
        "hardware": "Paired local MMLU-Pro study · same 16 H200 · official BTC quality decision remains unknown · handoff to unchanged OpenFOAM slide 35",
        "brief": "On the same 12,032 MMLU-Pro questions and 16 H200s, the optimised service got 9,452 correct versus 9,460 for stock FP8. That retains 99.9154% of reference accuracy, above our local 99% threshold.",
        "purpose": "Close the AI talk with the completed full-set local quality comparison. Distinguish absolute accuracy from accuracy retention, show that the two complete deployments were compared on the same H200 hardware and inputs, and keep the local point-gate result separate from the organisers’ unknown quality decision.",
        "visual": "The shared-input line reads “Same FP8 checkpoint · same prompts, generation and scoring”; the subtitle specifies 16 H200 GPUs, both complete deployments, and all 12,032 questions. Two columns compare stock reference (9,460/12,032 = 78.6237% accuracy) with the optimised service (9,452/12,032 = 78.5572%). Along the bottom, the left side gives “Accuracy retention = 9,452 / 9,460 = 99.9154%”; the right side shows PASS against the ≥99% threshold, plus 16/16 completed jobs and zero service errors. A neutral note says the organisers’ own quality decision remains separate. The oral handoff to OpenFOAM is unchanged.",
        "terms": [
            {"symbol": "accuracy", "meaning": "The share of the 12,032 questions answered correctly: correct answers divided by all questions."},
            {"symbol": "accuracy retention", "meaning": "Candidate accuracy divided by reference accuracy. Here the equal question denominators cancel, so retention is 9,452/9,460 = 99.9154%. It is not the percentage of questions the candidate answered correctly."},
            {"symbol": "stock FP8 reference", "meaning": "Our local stock deployment of the official Qwen3-235B FP8 checkpoint. It is the measured denominator for this comparison, not a numeric organiser-provided score."},
            {"symbol": "same 16 H200", "meaning": "Both complete deployments used the same two-node, sixteen-H200 cluster. The comparison is H200-to-H200; no H100 estimate is involved."},
            {"symbol": "local 99% point threshold", "meaning": "The predeclared rule that candidate accuracy divided by this measured stock-reference accuracy must be at least 0.99. Passing it is a local result, not BTC certification."},
        ],
        "reading": [
            "Read each accuracy as correct answers divided by all 12,032 questions: stock 9,460/12,032 = 78.623670%; candidate 9,452/12,032 = 78.557181%.",
            "The candidate has eight fewer correct answers, a net difference of 0.066489 percentage points. Accuracy retention is the ratio of the two accuracies, 9,452/9,460 = 99.915433%, which passes the local 99% point threshold.",
            "The net difference hides 876 discordant outcomes: 434 questions were candidate-only correct and 442 were reference-only correct. There were gains and losses across shards and categories.",
            "Computer science retained 338/345 = 97.971014% and philosophy 383/387 = 98.966408%. The declared gate is aggregate only; these category results remain limitations.",
            "Each role received all 12,032 questions once, split into eight fixed shards. All sixteen jobs completed and both roles had zero scored service errors. The 101 invalid parses per role were scored wrong. Answers reaching the generation cap (1,484 reference; 1,468 candidate) stayed in the denominator and were scored normally from their parsed answer, not automatically marked wrong.",
            "This is one complete pass per deployment, not repeated independent deployments. Raw-answer replay verifies scoring but is not a second GPU trial. The local MMLU-Pro pass does not certify BTC’s evaluation or predict unseen benchmarks.",
        ],
        "tradeoff": {
            "observation": "On identical 12,032-question inputs and the same 16 H200 GPUs, stock FP8 scored 9,460/12,032 (78.623670%) and the optimised deployment scored 9,452/12,032 (78.557181%). Both roles had zero scored service errors; all sixteen allocations completed.",
            "hypothesis": "The full local paired comparison tests whether the complete optimised serving implementation retains at least 99% of the measured stock deployment’s accuracy, while preserving every question and first response.",
            "conclusion": "The candidate retains 9,452/9,460 = 99.915433% of reference accuracy and passes the predeclared aggregate local 99% point threshold. This is a local MMLU-Pro result, not an organiser-certified result.",
            "unknown": "One complete pass per deployment does not establish statistical equivalence, identical answers, causality for any kernel or patch, or quality on unseen tasks. Category retention is below 99% in computer science and philosophy. BTC’s own quality outcome remains unknown.",
        },
        "reasoning": {
            "problem": "The accepted performance run proved that the service could meet its workload gates, but synthetic benchmark requests did not establish answer accuracy.",
            "why_it_matters": "Serving layout, kernels, batching and reductions can change generated answers even when the official checkpoint is retained. A quality claim therefore needs scored model answers, not only unchanged weights or good throughput.",
            "why_this_test": "Compare the stock official FP8 deployment with the accepted optimised service on the same two-node, 16-H200 hardware, identical pinned MMLU-Pro prompts and all 12,032 test questions. Keep the first response and use the frozen scorer. Count invalid parsed answers as wrong; keep length-capped answers in the denominator and score each parsed answer normally.",
            "what_we_learned": "The stock deployment answered 9,460/12,032 correctly (78.623670%); the candidate answered 9,452/12,032 correctly (78.557181%). Their accuracy ratio is 99.915433%, above the local 99% point threshold. There were 434 candidate-only correct and 442 reference-only correct outcomes, so the net loss of eight is not only eight changed questions. All sixteen jobs completed with zero scored service errors.",
            "next_logic": "Close the AI section with the bounded local pass and its limits: one pass per role, category losses, and no BTC certification. Then hand over to the unchanged OpenFOAM section.",
        },
        "script": "We tested the complete optimised service against a stock deployment of the same FP8 checkpoint, on the same sixteen H200 GPUs and all 12,032 MMLU-Pro questions. The stock deployment got 9,460 correct, or 78.62 percent. Our service got 9,452, or 78.56 percent. Dividing those accuracies gives 99.9154 percent retention, above our local 99 percent threshold. All sixteen jobs completed without scored service errors, and invalid answers stayed counted as wrong. This is one full local pass per deployment, not a BTC certificate or a guarantee for other benchmarks. I now hand over to OpenFOAM.",
        "caution": "Call 99.9154% accuracy retention, not candidate accuracy; candidate accuracy is 78.557181%. Do not say the services differed on only eight questions: 876 questions had discordant correctness outcomes. Do not present this local MMLU-Pro point-gate pass as BTC certification, statistical equivalence, causal attribution to one optimisation, or a guarantee on unseen tasks.",
        "transition": "The paired local quality check passes its aggregate point threshold, with its scope and limits clear. We now hand over to the unchanged OpenFOAM section.",
        "claim_type": "Local full-set quality measurement / claim boundary",
    },
    "vi": {
        "hardware": "Phép đo MMLU-Pro của nhóm trên cluster H200 · cùng 16 GPU · kết luận quality của BTC chưa rõ · bàn giao sang slide OpenFOAM 35 không đổi",
        "brief": "Trên cùng 12.032 câu MMLU-Pro và 16 H200, dịch vụ tối ưu trả lời đúng 9.452 câu, so với 9.460 của FP8 nguyên bản. Tỷ lệ giữ accuracy là 99,9154%, cao hơn ngưỡng kiểm tra của nhóm là 99%.",
        "purpose": "Khép lại phần AI bằng phép so sánh quality MMLU-Pro do nhóm tự đo trên cluster H200, dùng toàn bộ tập câu hỏi. Phân biệt accuracy tuyệt đối với tỷ lệ giữ accuracy, cho thấy hai deployment hoàn chỉnh được so trên cùng phần cứng và đầu vào, đồng thời tách kết quả ngưỡng kiểm tra của nhóm khỏi kết luận quality chưa biết của ban tổ chức.",
        "visual": "Dòng đầu vào chung ghi “Cùng checkpoint FP8 · cùng prompt, cách sinh và cách chấm”; phụ đề nêu 16 GPU H200, cả hai deployment hoàn chỉnh và đủ 12.032 câu hỏi. Hai cột so sánh FP8 nguyên bản (9.460/12.032 = 78,6237% accuracy) với dịch vụ tối ưu (9.452/12.032 = 78,5572%). Ở cuối slide, bên trái ghi “Tỷ lệ giữ accuracy = 9.452 / 9.460 = 99,9154%”; bên phải hiện PASS so với ngưỡng ≥99%, cùng 16/16 job hoàn tất và 0 lỗi dịch vụ. Một dòng trung tính nói kết luận quality riêng của ban tổ chức chưa được biết. Lời bàn giao sang OpenFOAM vẫn giữ nguyên.",
        "terms": [
            {"symbol": "accuracy", "meaning": "Tỷ lệ câu trả lời đúng trên toàn bộ 12.032 câu: số câu đúng chia cho tổng số câu."},
            {"symbol": "tỷ lệ giữ accuracy", "meaning": "Accuracy của ứng viên chia cho accuracy của tham chiếu. Vì hai mẫu số đều là 12.032, phép tính rút gọn thành 9.452/9.460 = 99,9154%. Đây không phải tỷ lệ câu hỏi mà ứng viên trả lời đúng."},
            {"symbol": "tham chiếu FP8 nguyên bản", "meaning": "Deployment nguyên bản của checkpoint Qwen3-235B FP8 chính thức, do nhóm đo trên cluster H200. Đây là mẫu số thực nghiệm của phép so sánh, không phải điểm số do ban tổ chức công bố."},
            {"symbol": "cùng 16 H200", "meaning": "Cả hai deployment hoàn chỉnh đều dùng cùng cụm hai nút, mười sáu H200. Đây là so sánh H200 với H200, không có ước tính từ H100."},
            {"symbol": "ngưỡng kiểm tra của nhóm 99%", "meaning": "Quy tắc định trước yêu cầu accuracy của ứng viên chia cho accuracy tham chiếu đo được phải đạt ít nhất 0,99. Đạt ngưỡng này là kết quả nhóm tự đo, không phải chứng nhận BTC."},
        ],
        "reading": [
            "Mỗi accuracy là số câu đúng chia cho toàn bộ 12.032 câu: FP8 nguyên bản 9.460/12.032 = 78,623670%; ứng viên 9.452/12.032 = 78,557181%.",
            "Ứng viên ít hơn tám câu đúng, chênh lệch ròng 0,066489 điểm phần trăm. Tỷ lệ giữ accuracy là tỷ số của hai accuracy, 9.452/9.460 = 99,915433%, đạt ngưỡng kiểm tra của nhóm 99%.",
            "Chênh lệch ròng che khuất 876 kết quả bất đồng: có 434 câu chỉ ứng viên trả lời đúng và 442 câu chỉ tham chiếu trả lời đúng. Có cả tăng lẫn giảm giữa các shard và hạng mục.",
            "Khoa học máy tính giữ 338/345 = 97,971014%; triết học giữ 383/387 = 98,966408%. Cổng đã định chỉ áp dụng cho tổng thể; đây vẫn là các giới hạn theo hạng mục.",
            "Mỗi vai trò nhận đủ 12.032 câu đúng một lần, chia thành tám shard cố định. Cả mười sáu job hoàn tất và hai vai trò đều không có lỗi dịch vụ được chấm. Câu trả lời không phân tích được (101 mỗi vai trò) được tính là sai. Câu chạm giới hạn sinh (1.484 tham chiếu; 1.468 ứng viên) vẫn nằm trong mẫu số và được chấm theo đáp án đã phân tích, không mặc định là sai.",
            "Mỗi deployment chỉ có một lượt hoàn chỉnh, không phải nhiều lần chạy độc lập. Phát lại câu trả lời thô xác minh cách chấm nhưng không phải lần chạy GPU thứ hai. Phép đo MMLU-Pro này do nhóm thực hiện trên cluster H200; nó không chứng nhận đánh giá của BTC hay dự đoán benchmark chưa kiểm tra.",
        ],
        "tradeoff": {
            "observation": "Trên cùng 12.032 câu hỏi và cùng 16 GPU H200, FP8 nguyên bản đạt 9.460/12.032 (78,623670%) còn deployment tối ưu đạt 9.452/12.032 (78,557181%). Cả hai vai trò không có lỗi dịch vụ được chấm; cả mười sáu allocation đã hoàn tất.",
            "hypothesis": "Phép so sánh đầy đủ có đối chứng do nhóm thực hiện trên cluster H200 kiểm tra liệu toàn bộ implementation serving tối ưu có giữ ít nhất 99% accuracy của deployment nguyên bản được đo hay không, trong khi giữ mọi câu hỏi và phản hồi đầu tiên.",
            "conclusion": "Ứng viên giữ 9.452/9.460 = 99,915433% accuracy tham chiếu và vượt ngưỡng kiểm tra tổng thể 99% đã định trước của nhóm. Đây là kết quả MMLU-Pro do nhóm tự đo trên cluster H200, không phải kết quả được ban tổ chức chứng nhận.",
            "unknown": "Một lượt hoàn chỉnh mỗi deployment không chứng minh tương đương thống kê, câu trả lời giống hệt, nguyên nhân từ kernel hay patch cụ thể, hoặc quality trên tác vụ chưa thấy. Tỷ lệ giữ theo hạng mục thấp hơn 99% ở khoa học máy tính và triết học. Kết quả quality riêng của BTC vẫn chưa biết.",
        },
        "reasoning": {
            "problem": "Lượt performance được chấp nhận chứng minh dịch vụ đạt cổng workload, nhưng yêu cầu tổng hợp của benchmark không đo accuracy câu trả lời.",
            "why_it_matters": "Layout serving, kernel, batching và phép reduction có thể làm đổi câu trả lời sinh ra dù vẫn giữ checkpoint chính thức. Vì vậy, tuyên bố về quality cần câu trả lời model được chấm, không chỉ trọng số không đổi hay throughput tốt.",
            "why_this_test": "So sánh deployment FP8 chính thức nguyên bản với dịch vụ tối ưu đã được chấp nhận trên cùng phần cứng hai nút, 16 H200, cùng prompt MMLU-Pro đã ghim phiên bản và toàn bộ 12.032 câu kiểm tra. Giữ phản hồi đầu tiên và dùng scorer đã cố định. Câu trả lời không phân tích được tính là sai; câu chạm giới hạn sinh vẫn nằm trong mẫu số và được chấm bình thường theo đáp án đã phân tích.",
            "what_we_learned": "Deployment nguyên bản trả lời đúng 9.460/12.032 câu (78,623670%); ứng viên đúng 9.452/12.032 câu (78,557181%). Tỷ số accuracy là 99,915433%, cao hơn ngưỡng kiểm tra của nhóm 99%. Có 434 câu chỉ ứng viên đúng và 442 câu chỉ tham chiếu đúng, nên mức giảm ròng tám câu không đồng nghĩa chỉ có tám câu khác kết quả. Cả mười sáu job hoàn tất và không có lỗi dịch vụ được chấm.",
            "next_logic": "Khép phần AI bằng kết quả nhóm tự đo trên cluster H200 với giới hạn rõ ràng: mỗi vai trò một lượt, có mất mát ở một số hạng mục, và không có chứng nhận BTC. Sau đó bàn giao sang phần OpenFOAM không đổi.",
        },
        "script": "Chúng tôi so sánh toàn bộ dịch vụ tối ưu với deployment nguyên bản của cùng checkpoint FP8, trên cùng mười sáu GPU H200 và đủ 12.032 câu MMLU-Pro. Bản nguyên bản trả lời đúng 9.460 câu, tức 78,62%. Dịch vụ của chúng tôi đúng 9.452 câu, tức 78,56%. Chia hai accuracy cho nhau, ta được tỷ lệ giữ 99,9154%, cao hơn ngưỡng kiểm tra của nhóm là 99%. Cả mười sáu job hoàn tất mà không có lỗi dịch vụ được chấm; câu trả lời không hợp lệ vẫn tính là sai. Câu chạm giới hạn sinh vẫn được chấm theo đáp án đã phân tích. Đây là một lượt đầy đủ cho mỗi deployment do nhóm tự đo trên cluster H200, không phải chứng nhận của BTC hay bảo đảm cho benchmark khác. Bây giờ tôi xin bàn giao sang phần OpenFOAM.",
        "caution": "Gọi 99,9154% là tỷ lệ giữ accuracy, không phải accuracy của ứng viên; accuracy ứng viên là 78,557181%. Không nói hai dịch vụ chỉ khác nhau ở tám câu: có 876 câu bất đồng về đúng/sai. Không trình bày phép đo này như chứng nhận BTC, tương đương thống kê, kết luận nhân quả cho một tối ưu riêng hay bảo đảm trên tác vụ chưa kiểm tra.",
        "transition": "Phép so sánh quality MMLU-Pro do nhóm tự đo trên cluster H200 đạt ngưỡng kiểm tra tổng thể, với phạm vi và giới hạn đã nêu. Bây giờ chúng tôi bàn giao sang phần OpenFOAM không đổi.",
        "claim_type": "Đo quality trên toàn bộ tập do nhóm thực hiện / giới hạn kết luận",
    },
}


def main() -> None:
    data = json.loads(TRANSCRIPT.read_text(encoding="utf-8"))
    by_slide = {record["slide"]: record for record in data}

    # Slide 16 is the sole full-row update in this script.
    by_slide[16].update(SLIDE_16)

    # Keep earlier setup claims current without changing the HPC handoff records.
    slide1 = by_slide[1]
    slide1["en"]["tradeoff"]["unknown"] = (
        "The local full-set MMLU-Pro point gate is now measured and passes; "
        "this service metric does not establish BTC certification or a contest ranking."
    )
    slide1["en"]["script"] = slide1["en"]["script"].replace(
        "Official model quality is a separate question.",
        "The local full-set quality check is reported at the end; it is separate from this service metric and does not certify the organiser’s result.",
    )
    slide1["vi"]["tradeoff"]["unknown"] = (
        "Cổng điểm MMLU-Pro cục bộ trên toàn bộ tập hiện đã được đo và đạt; "
        "chỉ số dịch vụ này không chứng minh BTC chứng nhận hay thứ hạng cuộc thi."
    )
    slide1["vi"]["script"] = slide1["vi"]["script"].replace(
        "Accuracy chính thức là câu hỏi riêng.",
        "Kết quả quality cục bộ trên toàn bộ tập được trình bày ở cuối; đó là phép đo riêng với chỉ số dịch vụ này và không chứng nhận kết quả của BTC.",
    )

    slide13 = by_slide[13]
    for lang, replacement in {
        "en": {
            "unknown": "The complete local MMLU-Pro comparison is reported on slide 16; BTC’s quality outcome remains unknown. The local result does not explain lower legacy replay variation or establish broader statistical repeatability.",
            "next_logic": "The package has one complete post-fix GPU acceptance run. Keep it separate from historical performance repeats; slide 16 reports the separately measured local full-set quality result and its limits.",
            "transition": "The successful portable entry closes the deployment-replay gap. The final slide reports the separate local full-set quality comparison and distinguishes it from BTC’s still-unknown decision.",
            "caution": "Do not merge the historical mean, native run and portable run into one statistical series. A single portable acceptance proves package execution once, not BTC quality certification or the cause of prior drift.",
        },
        "vi": {
            "unknown": "Phép so sánh MMLU-Pro cục bộ đầy đủ được trình bày ở slide 16; kết quả quality của BTC vẫn chưa biết. Kết quả cục bộ không giải thích biến động của replay cũ thấp hơn hay chứng minh tính lặp thống kê rộng hơn.",
            "next_logic": "Package có một lượt acceptance GPU đầy đủ sau sửa. Giữ riêng kết quả này với các lần đo performance lịch sử; slide 16 trình bày kết quả quality cục bộ trên toàn bộ tập và các giới hạn.",
            "transition": "Run portable thành công đóng khoảng trống replay deployment. Slide cuối trình bày phép so sánh quality cục bộ trên toàn bộ tập và phân biệt kết quả đó với quyết định của BTC vẫn chưa biết.",
            "caution": "Không gộp trung bình lịch sử, run native và run portable thành một chuỗi thống kê. Một lượt portable acceptance chứng minh package chạy được một lần, không chứng nhận quality của BTC hay giải thích nguyên nhân drift cũ.",
        },
    }.items():
        slide13[lang]["tradeoff"]["unknown"] = replacement["unknown"]
        slide13[lang]["reasoning"]["next_logic"] = replacement["next_logic"]
        slide13[lang]["transition"] = replacement["transition"]
        slide13[lang]["caution"] = replacement["caution"]

    TRANSCRIPT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
