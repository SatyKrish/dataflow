#!/usr/bin/env python3
"""
Entitlement Agent Implementation with LLM-Based Security Reasoning

Specialized agent for validating data access permissions and authorization.
Uses LLM to reason about security policies, compliance requirements, and access control strategies.
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from base_agent import BaseAgent
from db_client import AgentType

logger = logging.getLogger(__name__)

class EntitlementAgent(BaseAgent):
    """Agent specialized in validating data access permissions using LLM-based security reasoning"""
    
    def __init__(self):
        super().__init__(AgentType.ENTITLEMENT)
        self.security_frameworks = self._initialize_security_frameworks()
        self.compliance_policies = self._initialize_compliance_policies()
    
    def _initialize_security_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize security frameworks and access control models"""
        return {
            "rbac": {
                "name": "Role-Based Access Control",
                "description": "Access control based on user roles and permissions",
                "principles": ["least_privilege", "role_separation", "permission_inheritance"],
                "applicable_to": ["enterprise_data", "structured_data", "user_management"]
            },
            "abac": {
                "name": "Attribute-Based Access Control",
                "description": "Dynamic access control based on attributes and policies",
                "principles": ["context_aware", "fine_grained", "policy_driven"],
                "applicable_to": ["sensitive_data", "regulatory_compliance", "dynamic_environments"]
            },
            "data_classification": {
                "name": "Data Classification Security",
                "description": "Access control based on data sensitivity and classification",
                "principles": ["data_labeling", "graduated_access", "protection_levels"],
                "applicable_to": ["classified_data", "personal_information", "intellectual_property"]
            },
            "zero_trust": {
                "name": "Zero Trust Security Model",
                "description": "Never trust, always verify approach to access control",
                "principles": ["verify_explicitly", "least_privilege_access", "assume_breach"],
                "applicable_to": ["all_data_access", "external_systems", "high_security_environments"]
            }
        }
    
    def _initialize_compliance_policies(self) -> Dict[str, Dict[str, Any]]:
        """Initialize compliance and regulatory frameworks"""
        return {
            "gdpr": {
                "name": "General Data Protection Regulation",
                "scope": "EU personal data protection",
                "key_requirements": ["consent", "data_minimization", "right_to_erasure", "data_protection_by_design"],
                "data_types": ["personal_data", "sensitive_personal_data"],
                "restrictions": ["explicit_consent_required", "purpose_limitation", "retention_limits"]
            },
            "ccpa": {
                "name": "California Consumer Privacy Act", 
                "scope": "California consumer privacy rights",
                "key_requirements": ["right_to_know", "right_to_delete", "right_to_opt_out"],
                "data_types": ["personal_information", "consumer_data"],
                "restrictions": ["disclosure_requirements", "opt_out_rights", "data_sale_restrictions"]
            },
            "hipaa": {
                "name": "Health Insurance Portability and Accountability Act",
                "scope": "Protected health information",
                "key_requirements": ["minimum_necessary", "authorization", "safeguards"],
                "data_types": ["protected_health_information", "medical_records"],
                "restrictions": ["authorization_required", "minimum_necessary_standard", "audit_trails"]
            },
            "sox": {
                "name": "Sarbanes-Oxley Act",
                "scope": "Financial reporting and corporate governance",
                "key_requirements": ["internal_controls", "audit_trails", "segregation_of_duties"],
                "data_types": ["financial_data", "accounting_records", "corporate_governance"],
                "restrictions": ["audit_requirements", "segregation_of_duties", "retention_requirements"]
            }
        }
    
    async def _execute_logic(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute entitlement validation using LLM-based security reasoning"""
        
        # Step 1: LLM analyzes the access request and identifies security implications
        security_analysis = await self._llm_analyze_security_implications(task_description, context)
        
        # Step 2: LLM determines applicable compliance requirements
        compliance_analysis = await self._llm_analyze_compliance_requirements(security_analysis, task_description, context)
        
        # Step 3: LLM selects appropriate security frameworks and policies
        security_framework_selection = await self._llm_select_security_frameworks(security_analysis, compliance_analysis, context)
        
        # Step 4: LLM performs risk assessment
        risk_assessment = await self._llm_perform_risk_assessment(security_analysis, compliance_analysis, context)
        
        # Step 5: LLM makes access control decisions
        access_decision = await self._llm_make_access_decision(security_analysis, compliance_analysis, risk_assessment, context)
        
        # Step 6: LLM generates security recommendations and controls
        security_recommendations = await self._llm_generate_security_recommendations(access_decision, risk_assessment, context)
        
        return {
            "security_analysis": security_analysis,
            "compliance_analysis": compliance_analysis,
            "framework_selection": security_framework_selection,
            "risk_assessment": risk_assessment,
            "access_decision": access_decision,
            "security_recommendations": security_recommendations,
            "entitlement_summary": {
                "access_granted": access_decision.get("decision") == "approve",
                "risk_level": risk_assessment.get("overall_risk_level", "unknown"),
                "compliance_issues": len(compliance_analysis.get("violations", [])),
                "security_controls_required": len(security_recommendations.get("required_controls", [])),
                "frameworks_applied": len(security_framework_selection.get("selected_frameworks", []))
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _llm_analyze_security_implications(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to analyze security implications of the data access request"""
        
        system_prompt = """
        You are a cybersecurity specialist focused on data access security. Your job is to analyze data access requests and identify all security implications.

        Consider these security aspects:
        1. **Data Sensitivity**: What type of data is being requested and how sensitive is it?
        2. **Access Scope**: How broad or narrow is the data access request?
        3. **User Context**: Who is requesting access and what is their role/need?
        4. **Threat Vectors**: What security risks could this access create?
        5. **Data Flow**: How will the data be used, stored, or shared?

        Identify all potential security concerns and implications.
        """
        
        metadata_context = ""
        if context.get("metadata_results"):
            metadata_context = f"\nMetadata Discovery Results: {json.dumps(context['metadata_results'], indent=2)}"
        
        user_prompt = f"""
        Data Access Request: {task_description}
        
        Request Context:
        - User: {context.get('user_email', 'unknown')}
        - Query: {context.get('query', 'not provided')}
        - Session: {context.get('session_id', 'unknown')}
        {metadata_context}
        
        Analyze the security implications of this request in JSON format:
        {{
            "data_sensitivity_analysis": {{
                "data_types_identified": ["type1", "type2"],
                "sensitivity_levels": ["public", "internal", "confidential", "restricted"],
                "pii_indicators": ["indicator1", "indicator2"],
                "business_criticality": "low|medium|high|critical"
            }},
            "access_scope_analysis": {{
                "scope_breadth": "narrow|moderate|broad|unrestricted",
                "data_volume_estimate": "small|medium|large|massive",
                "temporal_scope": "point_in_time|historical|real_time|ongoing",
                "cross_system_access": true|false
            }},
            "user_context_analysis": {{
                "user_legitimacy": "verified|unverified|suspicious",
                "role_appropriateness": "appropriate|questionable|inappropriate",
                "need_to_know": "clear|unclear|unnecessary",
                "access_pattern": "normal|unusual|suspicious"
            }},
            "threat_identification": {{
                "insider_threat_risk": "low|medium|high",
                "data_exfiltration_risk": "low|medium|high", 
                "unauthorized_sharing_risk": "low|medium|high",
                "compliance_violation_risk": "low|medium|high"
            }},
            "security_concerns": ["concern1", "concern2"],
            "risk_indicators": ["indicator1", "indicator2"]
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1500)
            analysis = json.loads(llm_response)
            logger.info(f"Security analysis identified {len(analysis.get('security_concerns', []))} concerns")
            return analysis
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Security analysis failed: {e}, using fallback")
            return self._fallback_security_analysis(task_description, context)
    
    async def _llm_analyze_compliance_requirements(self, security_analysis: Dict[str, Any], task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to determine applicable compliance requirements"""
        
        system_prompt = f"""
        You are a compliance officer specializing in data protection regulations. Analyze data access requests for compliance requirements.

        Available Compliance Frameworks:
        {json.dumps(self.compliance_policies, indent=2)}

        Your job is to:
        1. Identify which compliance frameworks apply
        2. Determine specific requirements that must be met
        3. Identify potential compliance violations
        4. Recommend compliance controls
        """
        
        user_prompt = f"""
        Data Access Request: {task_description}
        Security Analysis: {json.dumps(security_analysis, indent=2)}
        Context: {json.dumps(context, indent=2)}
        
        Analyze compliance requirements in JSON format:
        {{
            "applicable_regulations": ["regulation1", "regulation2"],
            "regulation_analysis": {{
                "gdpr": {{
                    "applies": true|false,
                    "requirements": ["requirement1", "requirement2"],
                    "potential_violations": ["violation1", "violation2"]
                }},
                "ccpa": {{
                    "applies": true|false,
                    "requirements": ["requirement1", "requirement2"],
                    "potential_violations": ["violation1", "violation2"]
                }}
            }},
            "compliance_risk_level": "low|medium|high|critical",
            "required_controls": ["control1", "control2"],
            "documentation_requirements": ["document1", "document2"],
            "audit_implications": ["implication1", "implication2"],
            "violations": ["violation1", "violation2"],
            "recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1500)
            analysis = json.loads(llm_response)
            logger.info(f"Compliance analysis found {len(analysis.get('applicable_regulations', []))} applicable regulations")
            return analysis
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Compliance analysis failed: {e}, using fallback")
            return self._fallback_compliance_analysis(security_analysis, task_description)
    
    async def _llm_select_security_frameworks(self, security_analysis: Dict[str, Any], compliance_analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to select appropriate security frameworks and access control models"""
        
        system_prompt = f"""
        You are a security architect. Select the most appropriate security frameworks and access control models for this data access scenario.

        Available Security Frameworks:
        {json.dumps(self.security_frameworks, indent=2)}

        Consider:
        1. Data sensitivity and classification requirements
        2. Compliance obligations
        3. Risk levels and threat landscape
        4. Organizational security posture
        5. Technical feasibility and implementation complexity
        """
        
        user_prompt = f"""
        Security Analysis: {json.dumps(security_analysis, indent=2)}
        Compliance Analysis: {json.dumps(compliance_analysis, indent=2)}
        Context: {json.dumps(context, indent=2)}
        
        Select appropriate security frameworks in JSON format:
        {{
            "selected_frameworks": ["framework1", "framework2"],
            "framework_reasoning": {{
                "rbac": {{
                    "applicable": true|false,
                    "reasoning": "why this framework is or isn't suitable",
                    "implementation_priority": "high|medium|low"
                }},
                "abac": {{
                    "applicable": true|false,
                    "reasoning": "why this framework is or isn't suitable",
                    "implementation_priority": "high|medium|low"
                }}
            }},
            "primary_framework": "framework_name",
            "supporting_frameworks": ["framework1", "framework2"],
            "implementation_strategy": "sequential|parallel|phased",
            "complexity_assessment": "low|medium|high",
            "recommendations": ["recommendation1", "recommendation2"]
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1200)
            selection = json.loads(llm_response)
            logger.info(f"Selected {len(selection.get('selected_frameworks', []))} security frameworks")
            return selection
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Framework selection failed: {e}, using fallback")
            return self._fallback_framework_selection(security_analysis, compliance_analysis)
    
    async def _llm_perform_risk_assessment(self, security_analysis: Dict[str, Any], compliance_analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to perform comprehensive risk assessment"""
        
        system_prompt = """
        You are a risk assessment specialist. Perform a comprehensive risk assessment for this data access request.

        Evaluate these risk dimensions:
        1. **Confidentiality Risk**: Risk of unauthorized disclosure
        2. **Integrity Risk**: Risk of data tampering or corruption
        3. **Availability Risk**: Risk of data access disruption
        4. **Compliance Risk**: Risk of regulatory violations
        5. **Business Risk**: Risk to business operations and reputation
        6. **Technical Risk**: Risk from technical vulnerabilities

        Provide quantitative risk scores and qualitative assessments.
        """
        
        user_prompt = f"""
        Security Analysis: {json.dumps(security_analysis, indent=2)}
        Compliance Analysis: {json.dumps(compliance_analysis, indent=2)}
        Context: {json.dumps(context, indent=2)}
        
        Perform risk assessment in JSON format:
        {{
            "risk_dimensions": {{
                "confidentiality": {{
                    "score": 1-10,
                    "level": "low|medium|high|critical",
                    "factors": ["factor1", "factor2"],
                    "mitigation_required": true|false
                }},
                "integrity": {{
                    "score": 1-10,
                    "level": "low|medium|high|critical",
                    "factors": ["factor1", "factor2"],
                    "mitigation_required": true|false
                }},
                "availability": {{
                    "score": 1-10,
                    "level": "low|medium|high|critical",
                    "factors": ["factor1", "factor2"],
                    "mitigation_required": true|false
                }},
                "compliance": {{
                    "score": 1-10,
                    "level": "low|medium|high|critical",
                    "factors": ["factor1", "factor2"],
                    "mitigation_required": true|false
                }}
            }},
            "overall_risk_score": 1-10,
            "overall_risk_level": "low|medium|high|critical",
            "risk_tolerance": "acceptable|marginal|unacceptable",
            "key_risk_factors": ["factor1", "factor2"],
            "risk_mitigation_priority": "low|medium|high|urgent",
            "residual_risk_acceptable": true|false
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1500)
            assessment = json.loads(llm_response)
            logger.info(f"Risk assessment completed with overall risk level: {assessment.get('overall_risk_level', 'unknown')}")
            return assessment
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Risk assessment failed: {e}, using fallback")
            return self._fallback_risk_assessment(security_analysis, compliance_analysis)
    
    async def _llm_make_access_decision(self, security_analysis: Dict[str, Any], compliance_analysis: Dict[str, Any], risk_assessment: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to make the final access control decision"""
        
        system_prompt = """
        You are a security decision maker. Based on comprehensive security analysis, compliance requirements, and risk assessment, make an informed access control decision.

        Decision options:
        - **APPROVE**: Grant full access as requested
        - **APPROVE_WITH_CONDITIONS**: Grant access with specific security controls
        - **PARTIAL_APPROVE**: Grant limited/filtered access
        - **DENY**: Reject the access request
        - **ESCALATE**: Require additional approval or review

        Provide clear reasoning for your decision and specify any required controls.
        """
        
        user_prompt = f"""
        Security Analysis: {json.dumps(security_analysis, indent=2)}
        Compliance Analysis: {json.dumps(compliance_analysis, indent=2)}
        Risk Assessment: {json.dumps(risk_assessment, indent=2)}
        Context: {json.dumps(context, indent=2)}
        
        Make access control decision in JSON format:
        {{
            "decision": "approve|approve_with_conditions|partial_approve|deny|escalate",
            "decision_reasoning": "detailed explanation of the decision",
            "confidence_level": 0.0-1.0,
            "conditions": {{
                "required_controls": ["control1", "control2"],
                "access_limitations": ["limitation1", "limitation2"],
                "monitoring_requirements": ["requirement1", "requirement2"],
                "time_restrictions": "restriction_details",
                "data_filtering_required": true|false
            }},
            "approval_scope": {{
                "full_access": true|false,
                "filtered_access": true|false,
                "read_only": true|false,
                "time_limited": true|false
            }},
            "escalation_required": {{
                "required": true|false,
                "escalation_level": "supervisor|security_team|compliance_officer|executive",
                "escalation_reason": "reason for escalation"
            }},
            "review_requirements": {{
                "periodic_review": true|false,
                "review_frequency": "daily|weekly|monthly",
                "review_criteria": ["criteria1", "criteria2"]
            }},
            "justification": "business and security justification"
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1500)
            decision = json.loads(llm_response)
            logger.info(f"Access decision: {decision.get('decision', 'unknown')} with confidence {decision.get('confidence_level', 0)}")
            return decision
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Access decision failed: {e}, using fallback")
            return self._fallback_access_decision(risk_assessment)
    
    async def _llm_generate_security_recommendations(self, access_decision: Dict[str, Any], risk_assessment: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to generate security recommendations and implementation guidance"""
        
        system_prompt = """
        You are a security consultant. Based on the access decision and risk assessment, provide actionable security recommendations and implementation guidance.

        Focus on:
        1. **Immediate Controls**: Security controls that must be implemented immediately
        2. **Monitoring Strategy**: How to monitor and detect security issues
        3. **Incident Response**: How to respond to security incidents
        4. **Long-term Improvements**: Strategic security enhancements
        5. **Compliance Maintenance**: Ongoing compliance requirements
        """
        
        user_prompt = f"""
        Access Decision: {json.dumps(access_decision, indent=2)}
        Risk Assessment: {json.dumps(risk_assessment, indent=2)}
        Context: {json.dumps(context, indent=2)}
        
        Generate security recommendations in JSON format:
        {{
            "immediate_controls": {{
                "authentication": ["control1", "control2"],
                "authorization": ["control1", "control2"],
                "encryption": ["control1", "control2"],
                "logging": ["control1", "control2"]
            }},
            "monitoring_strategy": {{
                "real_time_monitoring": ["monitor1", "monitor2"],
                "anomaly_detection": ["detection1", "detection2"],
                "alert_thresholds": ["threshold1", "threshold2"],
                "reporting_requirements": ["report1", "report2"]
            }},
            "incident_response": {{
                "escalation_procedures": ["procedure1", "procedure2"],
                "containment_actions": ["action1", "action2"],
                "notification_requirements": ["requirement1", "requirement2"],
                "recovery_procedures": ["procedure1", "procedure2"]
            }},
            "compliance_maintenance": {{
                "audit_requirements": ["requirement1", "requirement2"],
                "documentation_needs": ["document1", "document2"],
                "training_requirements": ["training1", "training2"],
                "review_schedules": ["schedule1", "schedule2"]
            }},
            "long_term_improvements": ["improvement1", "improvement2"],
            "implementation_priority": "high|medium|low",
            "estimated_effort": "low|medium|high",
            "success_metrics": ["metric1", "metric2"]
        }}
        """
        
        try:
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1500)
            recommendations = json.loads(llm_response)
            logger.info(f"Generated security recommendations with {len(recommendations.get('immediate_controls', {}))} control categories")
            return recommendations
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Security recommendations failed: {e}, using fallback")
            return self._fallback_security_recommendations(access_decision, risk_assessment)
    
    def _fallback_security_analysis(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback security analysis when LLM fails"""
        return {
            "data_sensitivity_analysis": {
                "data_types_identified": ["unknown"],
                "sensitivity_levels": ["internal"],
                "business_criticality": "medium"
            },
            "threat_identification": {
                "insider_threat_risk": "medium",
                "data_exfiltration_risk": "medium"
            },
            "security_concerns": ["LLM analysis failed - manual review required"],
            "fallback": True
        }
    
    def _fallback_compliance_analysis(self, security_analysis: Dict[str, Any], task_description: str) -> Dict[str, Any]:
        """Fallback compliance analysis when LLM fails"""
        return {
            "applicable_regulations": ["general_data_protection"],
            "compliance_risk_level": "medium",
            "required_controls": ["access_logging", "data_minimization"],
            "violations": [],
            "fallback": True
        }
    
    def _fallback_framework_selection(self, security_analysis: Dict[str, Any], compliance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback framework selection when LLM fails"""
        return {
            "selected_frameworks": ["rbac"],
            "primary_framework": "rbac",
            "complexity_assessment": "medium",
            "fallback": True
        }
    
    def _fallback_risk_assessment(self, security_analysis: Dict[str, Any], compliance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback risk assessment when LLM fails"""
        return {
            "overall_risk_score": 5,
            "overall_risk_level": "medium",
            "risk_tolerance": "marginal",
            "key_risk_factors": ["analysis_failure", "unknown_data_sensitivity"],
            "fallback": True
        }
    
    def _fallback_access_decision(self, risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback access decision when LLM fails"""
        return {
            "decision": "approve_with_conditions",
            "decision_reasoning": "LLM analysis failed - applying conservative approval with standard controls",
            "confidence_level": 0.6,
            "conditions": {
                "required_controls": ["access_logging", "data_encryption", "regular_review"],
                "monitoring_requirements": ["access_monitoring", "anomaly_detection"]
            },
            "fallback": True
        }
    
    def _fallback_security_recommendations(self, access_decision: Dict[str, Any], risk_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback security recommendations when LLM fails"""
        return {
            "immediate_controls": {
                "authentication": ["multi_factor_authentication"],
                "authorization": ["role_based_access"],
                "logging": ["comprehensive_audit_logging"]
            },
            "monitoring_strategy": {
                "real_time_monitoring": ["access_monitoring"],
                "anomaly_detection": ["behavioral_analysis"]
            },
            "implementation_priority": "high",
            "fallback": True
        } 