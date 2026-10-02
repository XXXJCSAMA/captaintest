# Captain Test Skill Shop

发现和爬取
L1	Raw库	原始Git仓库数据，未做任何过滤	仅初步去重
L2	清洗库	通过英伟达安检规则校验后的数据	安全合规
L3	待入库库	AI生成简介、人工/算法优化后的数据	质量达标
L4	上架库	最终上线的成品，拆解为文件树	可装配运行
全链路追踪字段（每层都必须保留）：

source_repo：原始Git仓库

source_author：作者

source_commit：拉取时的commit hash

source_url：原始地址

crawled_at：爬取时间

目的：保证溯源可查，方便不同环节的人员接手。

五、七层过滤链路
text
Git仓库数据
   ↓
第1层：初步去重（按repo full_name去重）
   ↓
第2层：英伟达安检规则校验（可自定义扩展）
   ↓
第3层：AI判断生成Skill简介
   ↓
第4层：License合规判定
   ↓
第5层：语义去重（Embedding相似度）
   ↓
第6层：三维评分（Utility/Security/Provenance）
   ↓
第7层：人工抽检
   ↓
合规Skill资源集 → 进入待入库库
英伟达安检规则可自定义扩展：后续根据业务需求调整校验规则，适配不同阶段的筛选标准。

每个上架 skill 都有
score card + provenance + license + "recommended by"



