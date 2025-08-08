from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from models.project import Project
from models.keyword import Keyword
from models.crawling_result import CrawlingResult
from models.feature_analysis import FeatureAnalysis
from datetime import datetime

class ReportService:
    """리포트 생성 서비스 클래스"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """커스텀 스타일 설정"""
        # 제목 스타일
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # 중앙 정렬
        )
        
        # 섹션 제목 스타일
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20
        )
        
        # 일반 텍스트 스타일
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
    
    def generate_pdf_report(self, project_id):
        """PDF 리포트 생성"""
        # 프로젝트 정보 조회
        project = Project.query.get(project_id)
        if not project:
            raise ValueError("프로젝트를 찾을 수 없습니다.")
        
        # 데이터 조회
        keywords = Keyword.query.filter_by(project_id=project_id).all()
        crawling_results = CrawlingResult.query.filter_by(project_id=project_id).all()
        feature_analyses = FeatureAnalysis.query.filter_by(project_id=project_id).all()
        
        # PDF 생성
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # 제목
        story.append(Paragraph("Feature Detective 분석 리포트", self.title_style))
        story.append(Spacer(1, 20))
        
        # 프로젝트 정보
        story.append(Paragraph("프로젝트 정보", self.section_style))
        project_info = [
            ["프로젝트명", project.name],
            ["설명", project.description or "설명 없음"],
            ["생성일", project.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ["키워드 수", str(len(keywords))],
            ["분석 URL 수", str(len(crawling_results))],
            ["분석 결과 수", str(len(feature_analyses))]
        ]
        
        project_table = Table(project_info, colWidths=[2*inch, 4*inch])
        project_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(project_table)
        story.append(Spacer(1, 20))
        
        # 통계 요약
        story.append(Paragraph("분석 통계", self.section_style))
        support_stats = {
            'O': len([a for a in feature_analyses if a.support_status == 'O']),
            'X': len([a for a in feature_analyses if a.support_status == 'X']),
            '△': len([a for a in feature_analyses if a.support_status == '△'])
        }
        
        stats_info = [
            ["지원 (O)", str(support_stats['O'])],
            ["미지원 (X)", str(support_stats['X'])],
            ["부분 지원 (△)", str(support_stats['△'])],
            ["총 분석 수", str(sum(support_stats.values()))]
        ]
        
        stats_table = Table(stats_info, colWidths=[2*inch, 1*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # 키워드별 분석 결과
        story.append(Paragraph("키워드별 분석 결과", self.section_style))
        
        if keywords:
            keyword_data = [["키워드", "카테고리", "지원", "미지원", "부분지원", "총 분석"]]
            
            for keyword in keywords:
                keyword_analyses = [a for a in feature_analyses if a.keyword_id == keyword.id]
                supported = len([a for a in keyword_analyses if a.support_status == 'O'])
                not_supported = len([a for a in keyword_analyses if a.support_status == 'X'])
                partially_supported = len([a for a in keyword_analyses if a.support_status == '△'])
                
                keyword_data.append([
                    keyword.keyword,
                    keyword.category or "",
                    str(supported),
                    str(not_supported),
                    str(partially_supported),
                    str(len(keyword_analyses))
                ])
            
            keyword_table = Table(keyword_data, colWidths=[1.5*inch, 1*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
            keyword_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(keyword_table)
        else:
            story.append(Paragraph("등록된 키워드가 없습니다.", self.normal_style))
        
        story.append(Spacer(1, 20))
        
        # 상세 분석 결과 (최근 10개)
        story.append(Paragraph("상세 분석 결과 (최근 10개)", self.section_style))
        
        recent_analyses = sorted(feature_analyses, key=lambda x: x.analyzed_at, reverse=True)[:10]
        
        if recent_analyses:
            analysis_data = [["키워드", "URL", "지원여부", "신뢰도", "분석일시"]]
            
            for analysis in recent_analyses:
                keyword = next((k for k in keywords if k.id == analysis.keyword_id), None)
                keyword_text = keyword.keyword if keyword else "알 수 없음"
                
                # URL 축약
                url_short = analysis.url[:50] + "..." if len(analysis.url) > 50 else analysis.url
                
                analysis_data.append([
                    keyword_text,
                    url_short,
                    analysis.support_status,
                    f"{analysis.confidence_score:.2f}" if analysis.confidence_score else "0.00",
                    analysis.analyzed_at.strftime('%Y-%m-%d %H:%M')
                ])
            
            analysis_table = Table(analysis_data, colWidths=[1.2*inch, 2*inch, 0.8*inch, 0.8*inch, 1.2*inch])
            analysis_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(analysis_table)
        else:
            story.append(Paragraph("분석 결과가 없습니다.", self.normal_style))
        
        # 리포트 생성
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_csv_report(self, project_id):
        """CSV 리포트 생성"""
        # 프로젝트 정보 조회
        project = Project.query.get(project_id)
        if not project:
            raise ValueError("프로젝트를 찾을 수 없습니다.")
        
        # 데이터 조회
        keywords = Keyword.query.filter_by(project_id=project_id).all()
        feature_analyses = FeatureAnalysis.query.filter_by(project_id=project_id).all()
        
        # CSV 데이터 생성
        csv_data = []
        csv_data.append(['프로젝트명', '키워드', '카테고리', 'URL', '지원여부', '신뢰도', '분석일시'])
        
        for analysis in feature_analyses:
            keyword = next((k for k in keywords if k.id == analysis.keyword_id), None)
            if keyword:
                csv_data.append([
                    project.name,
                    keyword.keyword,
                    keyword.category or '',
                    analysis.url,
                    analysis.support_status,
                    analysis.confidence_score or 0,
                    analysis.analyzed_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
        
        return csv_data
