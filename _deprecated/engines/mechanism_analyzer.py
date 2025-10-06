"""
Mechanism Analyzer - 세계관 형성 메커니즘 분석
Cognitive biases, temporal patterns, structural flaws
"""

import logging
from typing import Dict, List
from datetime import datetime
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class MechanismAnalyzer:
    """Analyzes worldview formation mechanisms"""

    def analyze_mechanisms(self, perceptions: List[Dict]) -> Dict:
        """
        Analyze all formation mechanisms

        Args:
            perceptions: List of perceptions

        Returns:
            Dictionary with cognitive, temporal, and structural analysis
        """
        return {
            'cognitive_mechanisms': self.analyze_cognitive(perceptions),
            'formation_phases': self.analyze_temporal(perceptions),
            'structural_flaws': self.analyze_structural(perceptions)
        }

    def analyze_cognitive(self, perceptions: List[Dict]) -> List[Dict]:
        """
        Detect cognitive biases and psychological mechanisms

        Returns:
            List of detected mechanisms
        """
        mechanisms = []

        # 1. Confirmation Bias (확증편향)
        if self._uses_confirmation_bias(perceptions):
            mechanisms.append({
                'type': 'confirmation_bias',
                'name': '확증편향',
                'description': '일관되게 부정적/긍정적 정보만 제시하여 기존 편견 강화',
                'vulnerability': '사람들은 자신의 믿음을 확인하는 정보를 선호함',
                'strength': self._calculate_consistency(perceptions)
            })

        # 2. Availability Heuristic (가용성 휴리스틱)
        repetition_rate = self._calculate_repetition_rate(perceptions)
        if repetition_rate > 1.5:
            mechanisms.append({
                'type': 'availability_heuristic',
                'name': '가용성 휴리스틱',
                'description': f'동일한 주장을 {repetition_rate:.1f}배 반복하여 중요성 과장',
                'vulnerability': '자주 접한 정보를 더 중요하고 확실한 것으로 인식',
                'strength': min(repetition_rate / 5.0, 1.0)
            })

        # 3. Emotional Loading (감정 로딩)
        emotions = self._extract_emotions(perceptions)
        if emotions:
            mechanisms.append({
                'type': 'emotional_loading',
                'name': '감정 로딩',
                'description': f'{", ".join(emotions[:3])} 등 강한 감정으로 이성적 판단 방해',
                'vulnerability': '강한 감정은 비판적 사고 능력을 저하시킴',
                'emotions': emotions,
                'strength': min(len(emotions) / 5.0, 1.0)
            })

        # 4. False Dichotomy (이분법적 사고)
        if self._uses_false_dichotomy(perceptions):
            mechanisms.append({
                'type': 'false_dichotomy',
                'name': '이분법적 사고',
                'description': '복잡한 상황을 극단적인 양자택일로 단순화',
                'vulnerability': '중간 지대나 대안적 관점을 고려하지 못하게 함',
                'strength': 0.7
            })

        return mechanisms

    def analyze_temporal(self, perceptions: List[Dict]) -> List[Dict]:
        """
        Analyze temporal formation patterns

        Returns:
            List of formation phases
        """
        if not perceptions:
            return []

        # Sort by time
        timeline = sorted(perceptions, key=lambda p: p.get('created_at', ''))

        if len(timeline) < 3:
            return [{
                'phase': 'seed',
                'perception_count': len(timeline),
                'description': '초기 단계 (데이터 부족)'
            }]

        phases = []

        # Seed phase (first 20%)
        seed_count = max(1, len(timeline) // 5)
        seed = timeline[:seed_count]

        if seed:
            phases.append({
                'phase': 'seed',
                'perception_count': len(seed),
                'description': '초기 주장이 제시되는 씨앗 단계',
                'key_claims': self._extract_key_claims(seed)
            })

        # Growth phase (middle 60%)
        growth_start = seed_count
        growth_end = int(len(timeline) * 0.8)
        growth = timeline[growth_start:growth_end]

        if growth:
            tactics = self._detect_tactics(growth)
            phases.append({
                'phase': 'growth',
                'perception_count': len(growth),
                'description': '주장이 확산되고 변형되는 성장 단계',
                'tactics': tactics
            })

        # Peak phase (last 20%)
        peak = timeline[growth_end:]

        if peak:
            phases.append({
                'phase': 'peak',
                'perception_count': len(peak),
                'description': '주장이 정점에 도달한 단계',
                'platforms': self._count_sources(peak)
            })

        return phases

    def analyze_structural(self, perceptions: List[Dict]) -> List[Dict]:
        """
        Detect structural flaws in the worldview

        Returns:
            List of structural flaws
        """
        flaws = []

        # 1. Overgeneralization (과잉일반화)
        if self._has_overgeneralization(perceptions):
            flaws.append({
                'type': 'overgeneralization',
                'name': '과잉일반화',
                'description': '특정 사례를 전체로 일반화',
                'example': '일부 사례만으로 전체 집단을 판단',
                'counter': '개별 사례와 전체 집단을 구분해야 함'
            })

        # 2. Missing Evidence (증거 부족)
        if self._lacks_evidence(perceptions):
            flaws.append({
                'type': 'missing_evidence',
                'name': '증거 부족',
                'description': '검증 가능한 증거 없이 주장만 반복',
                'example': '구체적 출처나 데이터 없이 단정적 주장',
                'counter': '주장의 근거와 출처를 요구해야 함'
            })

        # 3. Circular Reasoning (순환논증)
        if self._has_circular_reasoning(perceptions):
            flaws.append({
                'type': 'circular_reasoning',
                'name': '순환논증',
                'description': '결론을 전제로 사용하는 논리적 오류',
                'example': 'A이기 때문에 B다 → B이기 때문에 A다',
                'counter': '독립적인 증거를 요구해야 함'
            })

        # 4. Cherry Picking (체리피킹)
        if len(perceptions) > 5:
            flaws.append({
                'type': 'cherry_picking',
                'name': '체리피킹',
                'description': '유리한 정보만 선택적으로 제시',
                'example': '반대 증거나 맥락은 무시',
                'counter': '전체적인 맥락과 반대 증거도 확인해야 함'
            })

        return flaws

    # Helper methods

    def _uses_confirmation_bias(self, perceptions: List[Dict]) -> bool:
        """Check if consistently biased"""
        if not perceptions:
            return False

        valences = [p.get('perceived_valence', 'neutral') for p in perceptions]
        dominant = max(set(valences), key=valences.count)
        consistency = valences.count(dominant) / len(valences)

        return consistency > 0.7 and dominant != 'neutral'

    def _calculate_consistency(self, perceptions: List[Dict]) -> float:
        """Calculate valence consistency"""
        if not perceptions:
            return 0.0

        valences = [p.get('perceived_valence', 'neutral') for p in perceptions]
        dominant = max(set(valences), key=valences.count)
        return valences.count(dominant) / len(valences)

    def _calculate_repetition_rate(self, perceptions: List[Dict]) -> float:
        """Calculate claim repetition rate"""
        if not perceptions:
            return 0.0

        all_claims = []
        for p in perceptions:
            all_claims.extend(p.get('claims', []))

        if not all_claims:
            return 0.0

        unique_claims = len(set(all_claims))
        return len(all_claims) / max(unique_claims, 1)

    def _extract_emotions(self, perceptions: List[Dict]) -> List[str]:
        """Extract all unique emotions"""
        emotions = set()
        for p in perceptions:
            emotions.update(p.get('emotions', []))
        return list(emotions)

    def _uses_false_dichotomy(self, perceptions: List[Dict]) -> bool:
        """Check for false dichotomy patterns"""
        # Simple heuristic: high consistency + negative valence
        if not perceptions:
            return False

        consistency = self._calculate_consistency(perceptions)
        return consistency > 0.8

    def _extract_key_claims(self, perceptions: List[Dict]) -> List[str]:
        """Extract most common claims"""
        all_claims = []
        for p in perceptions:
            all_claims.extend(p.get('claims', []))

        counter = Counter(all_claims)
        return [claim for claim, count in counter.most_common(3)]

    def _detect_tactics(self, perceptions: List[Dict]) -> List[str]:
        """Detect spread tactics"""
        tactics = []

        # Repetition
        if self._calculate_repetition_rate(perceptions) > 2:
            tactics.append('repetition')

        # Variation (different claims on same subject)
        subjects = [p.get('perceived_subject', '') for p in perceptions]
        attributes = [p.get('perceived_attribute', '') for p in perceptions]

        if len(set(subjects)) < len(subjects) / 2 and len(set(attributes)) > len(subjects) / 2:
            tactics.append('variation')

        # Amplification (increasing emotions)
        emotions_over_time = [len(p.get('emotions', [])) for p in perceptions]
        if len(emotions_over_time) > 1 and emotions_over_time[-1] > emotions_over_time[0]:
            tactics.append('amplification')

        return tactics or ['steady_spread']

    def _count_sources(self, perceptions: List[Dict]) -> int:
        """Count unique content sources"""
        content_ids = set(p.get('content_id', '') for p in perceptions)
        return len(content_ids)

    def _has_overgeneralization(self, perceptions: List[Dict]) -> bool:
        """Check for overgeneralization"""
        # Heuristic: small sample but strong claims
        return len(perceptions) < 10 and self._calculate_consistency(perceptions) > 0.8

    def _lacks_evidence(self, perceptions: List[Dict]) -> bool:
        """Check if evidence is missing"""
        # Most perceptions lack specific claims
        perceptions_with_claims = sum(1 for p in perceptions if len(p.get('claims', [])) > 0)
        return perceptions_with_claims / max(len(perceptions), 1) < 0.5

    def _has_circular_reasoning(self, perceptions: List[Dict]) -> bool:
        """Check for circular reasoning patterns"""
        # Simplified: high repetition of same claims
        return self._calculate_repetition_rate(perceptions) > 3
