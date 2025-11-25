#!/usr/bin/env python3
"""
智能化预测和问题预防引擎
基于历史数据和机器学习预测开发中的问题
"""

import json
import statistics
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

from intelligent_engine import IntelligentEngine, ProjectType, DeveloperProfile


@dataclass
class RiskFactor:
    """风险因子"""
    category: str
    description: str
    probability: float  # 0-1
    impact: str  # low/medium/high/critical
    mitigation: List[str]
    early_indicators: List[str]


@dataclass
class PredictionResult:
    """预测结果"""
    success_probability: float
    estimated_duration: int
    predicted_issues: List[RiskFactor]
    confidence_level: float
    recommendations: List[str]


class PredictionEngine:
    """预测引擎"""

    def __init__(self, engine: IntelligentEngine):
        self.engine = engine
        self.plugin_root = Path(engine.plugin_root)
        self.prediction_dir = self.plugin_root / "data" / "predictions"
        self.prediction_dir.mkdir(parents=True, exist_ok=True)

        # 风险模式库
        self.risk_patterns = self._load_risk_patterns()

        # 历史成功/失败数据
        self.historical_data = self._load_historical_data()

        # 技术复杂度指标
        self.complexity_indicators = self._init_complexity_indicators()

    def _load_risk_patterns(self) -> Dict:
        """加载风险模式"""
        patterns_file = self.prediction_dir / "risk_patterns.json"

        if patterns_file.exists():
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载风险模式失败: {e}")

        # 默认风险模式
        return {
            "technical_risks": {
                "scope_creep": {
                    "indicators": ["功能", "增加", "扩展", "补充"],
                    "probability_base": 0.3,
                    "mitigation": ["明确需求边界", "设置功能优先级", "分阶段实现"]
                },
                "technical_debt": {
                    "indicators": ["快速", "临时", "简单", "暂时"],
                    "probability_base": 0.4,
                    "mitigation": ["预留重构时间", "代码审查", "技术选型评估"]
                },
                "integration_challenges": {
                    "indicators": ["第三方", "接口", "集成", "连接"],
                    "probability_base": 0.25,
                    "mitigation": ["API文档审查", "备用方案", "集成测试"]
                }
            },
            "timeline_risks": {
                "underestimation": {
                    "indicators": ["简单", "容易", "快速", "很快"],
                    "probability_base": 0.35,
                    "mitigation": ["详细任务分解", "缓冲时间", "里程碑检查"]
                },
                "scope_expansion": {
                    "indicators": ["完善", "优化", "增强", "改进"],
                    "probability_base": 0.3,
                    "mitigation": ["变更控制", "版本管理", "需求冻结点"]
                }
            },
            "quality_risks": {
                "insufficient_testing": {
                    "indicators": ["测试", "验证", "检查"],
                    "probability_base": 0.4,
                    "mitigation": ["测试计划", "自动化测试", "代码覆盖率"]
                },
                "performance_issues": {
                    "indicators": ["性能", "速度", "响应", "效率"],
                    "probability_base": 0.25,
                    "mitigation": ["性能基准", "压力测试", "优化策略"]
                }
            }
        }

    def _load_historical_data(self) -> Dict:
        """加载历史数据"""
        history_file = self.prediction_dir / "historical_data.json"

        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载历史数据失败: {e}")

        return {
            "projects": [],
            "success_patterns": {},
            "failure_patterns": {}
        }

    def _init_complexity_indicators(self) -> Dict:
        """初始化复杂度指标"""
        return {
            "technical_keywords": {
                "high": ["微服务", "分布式", "高并发", "大数据", "机器学习", "区块链"],
                "medium": ["API", "数据库", "缓存", "消息队列", "异步"],
                "low": ["CRUD", "简单", "基础", "原型"]
            },
            "scope_keywords": {
                "high": ["完整系统", "企业级", "大规模", "综合性", "平台化"],
                "medium": ["管理系统", "标准应用", "功能完整"],
                "low": ["简单工具", "原型", "演示", "基础功能"]
            },
            "integration_keywords": {
                "high": ["多个系统", "第三方", "外部API", "数据同步"],
                "medium": ["数据库", "文件系统", "网络请求"],
                "low": ["本地处理", "单机", "独立应用"]
            }
        }

    def predict_project_outcomes(self, project_description: str, project_type: ProjectType) -> PredictionResult:
        """预测项目结果"""
        # 分析项目复杂度
        complexity_score = self._analyze_complexity(project_description, project_type)

        # 基于历史数据预测成功率
        success_prob = self._predict_success_probability(project_type, complexity_score)

        # 预测开发时间
        estimated_duration = self._predict_duration(project_type, complexity_score, project_description)

        # 预测潜在问题
        predicted_issues = self._predict_issues(project_description, project_type, complexity_score)

        # 计算预测置信度
        confidence = self._calculate_confidence(project_type, complexity_score)

        # 生成推荐建议
        recommendations = self._generate_recommendations(predicted_issues, project_type, complexity_score)

        return PredictionResult(
            success_probability=success_prob,
            estimated_duration=estimated_duration,
            predicted_issues=predicted_issues,
            confidence_level=confidence,
            recommendations=recommendations
        )

    def _analyze_complexity(self, description: str, project_type: ProjectType) -> float:
        """分析项目复杂度"""
        description_lower = description.lower()
        complexity_score = 0.5  # 基础分数

        # 技术复杂度分析
        for level, keywords in self.complexity_indicators["technical_keywords"].items():
            matches = sum(1 for keyword in keywords if keyword in description_lower)
            if level == "high" and matches > 0:
                complexity_score += 0.3 * min(matches, 3)
            elif level == "medium" and matches > 0:
                complexity_score += 0.15 * min(matches, 2)
            elif level == "low" and matches > 0:
                complexity_score -= 0.1 * min(matches, 2)

        # 范围复杂度分析
        for level, keywords in self.complexity_indicators["scope_keywords"].items():
            matches = sum(1 for keyword in keywords if keyword in description_lower)
            if level == "high" and matches > 0:
                complexity_score += 0.25 * min(matches, 3)
            elif level == "medium" and matches > 0:
                complexity_score += 0.1 * min(matches, 2)

        # 集成复杂度分析
        for level, keywords in self.complexity_indicators["integration_keywords"].items():
            matches = sum(1 for keyword in keywords if keyword in description_lower)
            if level == "high" and matches > 0:
                complexity_score += 0.2 * min(matches, 2)
            elif level == "medium" and matches > 0:
                complexity_score += 0.1 * min(matches, 2)

        # 项目类型调整
        type_adjustments = {
            ProjectType.WEB_APP: 0.1,
            ProjectType.API_SERVICE: 0.05,
            ProjectType.MOBILE_APP: 0.15,
            ProjectType.CLI_TOOL: -0.1,
            ProjectType.AUTOMATION: 0.0
        }

        complexity_score += type_adjustments.get(project_type, 0)

        # 限制范围
        return max(0.0, min(1.0, complexity_score))

    def _predict_success_probability(self, project_type: ProjectType, complexity_score: float) -> float:
        """预测成功概率"""
        # 基础成功率
        base_success_rates = {
            ProjectType.WEB_APP: 0.75,
            ProjectType.API_SERVICE: 0.80,
            ProjectType.CLI_TOOL: 0.85,
            ProjectType.MOBILE_APP: 0.70,
            ProjectType.AUTOMATION: 0.82
        }

        base_rate = base_success_rates.get(project_type, 0.75)

        # 复杂度调整
        complexity_adjustment = (1 - complexity_score) * 0.3  # 复杂度越低，成功率越高

        # 用户历史经验调整
        user_experience_factor = self._calculate_user_experience_factor(project_type)

        # 计算最终成功率
        success_probability = base_rate + complexity_adjustment + user_experience_factor

        # 基于历史数据微调
        historical_factor = self._get_historical_success_factor(project_type)
        success_probability *= historical_factor

        return max(0.3, min(0.95, success_probability))  # 限制在合理范围

    def _calculate_user_experience_factor(self, project_type: ProjectType) -> float:
        """计算用户经验因子"""
        profile = self.engine.profile
        type_key = project_type.value

        if type_key not in profile.project_preferences:
            return 0.0

        # 基于项目数量和成功率
        preference = profile.project_preferences[type_key]
        frequency = preference.get("frequency", 0)
        avg_satisfaction = preference.get("avg_satisfaction", 3.0)

        # 项目经验因子
        experience_factor = min(frequency / 10.0, 0.15)  # 最多提升15%

        # 满意度因子
        satisfaction_factor = (avg_satisfaction - 3.0) / 10.0  # 基于满意度调整

        return experience_factor + satisfaction_factor

    def _get_historical_success_factor(self, project_type: ProjectType) -> float:
        """获取历史成功因子"""
        type_key = project_type.value

        # 从历史数据中查找类似项目
        similar_projects = [
            p for p in self.historical_data.get("projects", [])
            if p.get("project_type") == type_key
        ]

        if not similar_projects:
            return 1.0  # 没有历史数据，使用默认因子

        # 计算平均成功率
        success_projects = sum(1 for p in similar_projects if p.get("success", False))
        success_rate = success_projects / len(similar_projects)

        # 转换为调整因子
        if success_rate > 0.8:
            return 1.05  # 历史成功率高，略微提升
        elif success_rate < 0.6:
            return 0.95  # 历史成功率低，略微降低
        else:
            return 1.0  # 中等成功率，不调整

    def _predict_duration(self, project_type: ProjectType, complexity_score: float, description: str) -> int:
        """预测开发时间"""
        # 基础时间
        base_times = {
            ProjectType.WEB_APP: 120,
            ProjectType.API_SERVICE: 100,
            ProjectType.CLI_TOOL: 60,
            ProjectType.MOBILE_APP: 180,
            ProjectType.AUTOMATION: 90
        }

        base_time = base_times.get(project_type, 120)

        # 复杂度调整
        complexity_multiplier = 1.0 + (complexity_score * 1.5)  # 复杂度最高可增加150%时间

        # 用户历史调整
        user_multiplier = self._get_user_time_multiplier(project_type)

        # 功能点数量调整
        feature_count = self._count_features(description)
        feature_multiplier = 1.0 + (feature_count * 0.1)  # 每个功能点增加10%时间

        predicted_time = int(base_time * complexity_multiplier * user_multiplier * feature_multiplier)

        # 基于历史数据微调
        historical_time_factor = self._get_historical_time_factor(project_type)
        predicted_time = int(predicted_time * historical_time_factor)

        return predicted_time

    def _get_user_time_multiplier(self, project_type: ProjectType) -> float:
        """获取用户时间调整因子"""
        profile = self.engine.profile
        type_key = project_type.value

        if type_key not in profile.project_preferences:
            return 1.0

        avg_time = profile.project_preferences[type_key].get("avg_time")
        if not avg_time:
            return 1.0

        # 与标准时间比较
        standard_times = {
            "web_app": 120,
            "api_service": 100,
            "cli_tool": 60,
            "mobile_app": 180,
            "automation": 90
        }

        standard_time = standard_times.get(type_key, 120)
        return avg_time / standard_time

    def _count_features(self, description: str) -> int:
        """计算功能点数量"""
        feature_indicators = [
            r"功能.*?[:：]",
            r"模块.*?[:：]",
            r"特性.*?[:：]",
            r"实现.*?[:：]",
            r"支持.*?[:：]",
            r"第.*?个",
            r"\d+\.",
            r"•\s*",
            r"-\s*"
        ]

        feature_count = 0
        for pattern in feature_indicators:
            matches = re.findall(pattern, description)
            feature_count += len(matches)

        # 根据描述长度估算
        word_count = len(description.split())
        if word_count > 100:
            feature_count += int(word_count / 50)

        return min(feature_count, 20)  # 最多20个功能点

    def _get_historical_time_factor(self, project_type: ProjectType) -> float:
        """获取历史时间因子"""
        type_key = project_type.value

        similar_projects = [
            p for p in self.historical_data.get("projects", [])
            if p.get("project_type") == type_key and p.get("estimated_time") and p.get("actual_time")
        ]

        if not similar_projects:
            return 1.0

        # 计算实际时间与预估时间的比率
        ratios = [p["actual_time"] / p["estimated_time"] for p in similar_projects]
        avg_ratio = statistics.mean(ratios)

        return avg_ratio

    def _predict_issues(self, description: str, project_type: ProjectType, complexity_score: float) -> List[RiskFactor]:
        """预测潜在问题"""
        predicted_issues = []

        description_lower = description.lower()

        # 基于风险模式预测
        for category, risks in self.risk_patterns.items():
            for risk_name, risk_data in risks.items():
                # 检查指标词
                indicator_matches = sum(1 for indicator in risk_data["indicators"] if indicator in description_lower)

                if indicator_matches > 0:
                    # 计算概率
                    base_probability = risk_data["probability_base"]
                    indicator_bonus = min(indicator_matches * 0.1, 0.3)  # 最多增加30%
                    complexity_bonus = complexity_score * 0.2  # 复杂度越高，风险越大

                    probability = min(base_probability + indicator_bonus + complexity_bonus, 0.9)

                    # 确定影响级别
                    impact = self._determine_impact_level(category, probability, complexity_score)

                    # 生成早期预警指标
                    early_indicators = self._generate_early_indicators(category, risk_name, description_lower)

                    risk_factor = RiskFactor(
                        category=category,
                        description=risk_name.replace("_", " ").title(),
                        probability=probability,
                        impact=impact,
                        mitigation=risk_data["mitigation"],
                        early_indicators=early_indicators
                    )

                    predicted_issues.append(risk_factor)

        # 基于用户历史问题预测
        historical_issues = self._predict_from_historical_issues(project_type)
        predicted_issues.extend(historical_issues)

        # 按概率排序并返回前5个
        predicted_issues.sort(key=lambda x: x.probability, reverse=True)
        return predicted_issues[:5]

    def _determine_impact_level(self, category: str, probability: float, complexity_score: float) -> str:
        """确定影响级别"""
        # 基础影响级别
        base_impacts = {
            "technical_risks": "high",
            "timeline_risks": "medium",
            "quality_risks": "medium"
        }

        base_impact = base_impacts.get(category, "medium")

        # 根据概率和复杂度调整
        if probability > 0.7 or complexity_score > 0.8:
            return "critical"
        elif probability > 0.5 or complexity_score > 0.6:
            return "high"
        elif probability > 0.3 or complexity_score > 0.4:
            return "medium"
        else:
            return "low"

    def _generate_early_indicators(self, category: str, risk_name: str, description: str) -> List[str]:
        """生成早期预警指标"""
        indicators = []

        # 基于风险类型的通用指标
        if category == "technical_risks":
            if "scope" in risk_name:
                indicators.extend(["需求频繁变更", "功能点持续增加", "边界不清晰"])
            elif "debt" in risk_name:
                indicators.extend(["临时解决方案增多", "代码注释缺失", "重复代码出现"])
            elif "integration" in risk_name:
                indicators.extend(["第三方API响应慢", "数据格式不匹配", "连接稳定性问题"])

        elif category == "timeline_risks":
            indicators.extend(["里程碑延期", "任务完成时间超出预期", "依赖任务阻塞"])

        elif category == "quality_risks":
            if "testing" in risk_name:
                indicators.extend(["测试用例覆盖率低", "Bug发现率增加", "回归测试不充分"])
            elif "performance" in risk_name:
                indicators.extend(["响应时间增长", "内存使用上升", "CPU占用增高"])

        return indicators

    def _predict_from_historical_issues(self, project_type: ProjectType) -> List[RiskFactor]:
        """基于历史问题预测"""
        type_key = project_type.value

        # 获取用户历史痛点
        profile = self.engine.profile
        pain_points = profile.work_patterns.get("common_pain_points", [])

        predicted_issues = []
        for pain_point in pain_points:
            # 转换为风险因子
            if "需求" in pain_point:
                risk = RiskFactor(
                    category="quality_risks",
                    description="需求理解偏差",
                    probability=0.4,
                    impact="medium",
                    mitigation=["详细需求确认", "原型验证", "用户反馈"],
                    early_indicators=["需求频繁变更", "理解不一致", "预期差异"]
                )
            elif "测试" in pain_point:
                risk = RiskFactor(
                    category="quality_risks",
                    description="测试不充分",
                    probability=0.35,
                    impact="medium",
                    mitigation=["测试计划", "自动化测试", "代码审查"],
                    early_indicators=["Bug发现滞后", "覆盖率不足", "回归问题"]
                )
            elif "性能" in pain_point:
                risk = RiskFactor(
                    category="quality_risks",
                    description="性能问题",
                    probability=0.3,
                    impact="high",
                    mitigation=["性能基准测试", "优化策略", "监控机制"],
                    early_indicators=["响应变慢", "资源占用高", "用户体验下降"]
                )
            else:
                continue

            predicted_issues.append(risk)

        return predicted_issues

    def _calculate_confidence(self, project_type: ProjectType, complexity_score: float) -> float:
        """计算预测置信度"""
        confidence_factors = []

        # 基于历史数据量
        similar_projects = len([
            p for p in self.historical_data.get("projects", [])
            if p.get("project_type") == project_type.value
        ])
        data_confidence = min(similar_projects / 10.0, 0.3)  # 最多30%
        confidence_factors.append(data_confidence)

        # 基于用户经验
        profile = self.engine.profile
        type_key = project_type.value
        if type_key in profile.project_preferences:
            experience = profile.project_preferences[type_key].get("frequency", 0)
            experience_confidence = min(experience / 5.0, 0.3)  # 最多30%
            confidence_factors.append(experience_confidence)

        # 基于描述清晰度
        description_clarity = 1.0 - (complexity_score * 0.2)  # 复杂度越低，描述可能越清晰
        confidence_factors.append(description_clarity * 0.2)

        # 基础置信度
        confidence_factors.append(0.3)

        return min(sum(confidence_factors), 0.9)  # 最多90%置信度

    def _generate_recommendations(self, issues: List[RiskFactor], project_type: ProjectType, complexity_score: float) -> List[str]:
        """生成推荐建议"""
        recommendations = []

        # 基于预测问题的建议
        if issues:
            high_impact_issues = [issue for issue in issues if issue.impact in ["high", "critical"]]
            if high_impact_issues:
                recommendations.append(f"重点关注高影响风险：{', '.join([issue.description for issue in high_impact_issues[:2]])}")

            # 收集所有缓解措施
            all_mitigations = []
            for issue in issues:
                all_mitigations.extend(issue.mitigation)

            # 统计最常用的缓解措施
            mitigation_counts = Counter(all_mitigations)
            common_mitigations = [mitigation for mitigation, count in mitigation_counts.most_common(3)]
            if common_mitigations:
                recommendations.append(f"推荐采取以下预防措施：{', '.join(common_mitigations)}")

        # 基于复杂度的建议
        if complexity_score > 0.7:
            recommendations.append("高复杂度项目，建议分阶段实施，设置中间里程碑")
        elif complexity_score < 0.3:
            recommendations.append("低复杂度项目，可以快速迭代，重点关注用户体验")

        # 基于项目类型的建议
        type_recommendations = {
            "web_app": ["重视用户体验设计", "考虑SEO优化", "预留性能优化空间"],
            "api_service": ["重点设计API文档", "考虑版本管理", "重视安全性"],
            "cli_tool": ["重视帮助文档", "考虑跨平台兼容", "优化错误提示"],
            "mobile_app": ["关注电池消耗", "考虑离线功能", "优化启动速度"],
            "automation": ["重视异常处理", "添加详细日志", "考虑监控告警"]
        }

        if project_type.value in type_recommendations:
            recommendations.extend(type_recommendations[project_type.value])

        return recommendations[:5]  # 最多5个建议

    def record_prediction_accuracy(self, prediction: PredictionResult, actual_results: Dict):
        """记录预测准确性"""
        accuracy_record = {
            "timestamp": datetime.now().isoformat(),
            "prediction": asdict(prediction),
            "actual_results": actual_results,
            "success": actual_results.get("success", False),
            "actual_duration": actual_results.get("duration", 0),
            "issues_encountered": actual_results.get("issues", [])
        }

        # 保存到历史数据
        self.historical_data["projects"].append(accuracy_record)

        # 更新历史数据文件
        history_file = self.prediction_dir / "historical_data.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.historical_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"保存历史数据失败: {e}")

        # 更新风险模式
        self._update_risk_patterns(accuracy_record)

    def _update_risk_patterns(self, accuracy_record: Dict):
        """基于准确性更新风险模式"""
        actual_issues = accuracy_record.get("actual_results", {}).get("issues", [])
        predicted_issues = accuracy_record["prediction"]["predicted_issues"]

        # 分析预测准确性
        for predicted_issue in predicted_issues:
            category = predicted_issue["category"]
            description = predicted_issue["description"]

            # 检查是否预测准确
            was_predicted = any(
                category.lower() in issue.lower() or description.lower() in issue.lower()
                for issue in actual_issues
            )

            if category in self.risk_patterns:
                # 更新模式库（这里可以实现更复杂的学习逻辑）
                pass