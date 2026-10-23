from security import UserContext
from report_generat import ReportGenerat, Report
from agnet_planner import PlanGenerate, ResultSummarizer, StepExecute
from query_decomposer import QureyAnalyse




class PlanAndExecuteAgnet:
    def __init__(
            self,
            query_analyse: QureyAnalyse  |None=None,
            plan_generate: PlanGenerate |None=None,
            step_execute: StepExecute |None=None,
            result_summarizer: ResultSummarizer |None=None,
            report_generat: ReportGenerat |None=None
        ):
        self.query_analyse=query_analyse or QureyAnalyse()
        self.plan_generate=plan_generate or  PlanGenerate()
        self.step_execute=step_execute or StepExecute()
        self.result_summarizer=result_summarizer or ResultSummarizer()
        self.report_generat=report_generat or ReportGenerat()

    def agnet_run(self,query: str,user_contest: UserContext) -> Report:
        decomposition_plan=self.query_analyse.run_retry(query)
        plan_step=self.plan_generate.PlanGenerate(decomposition_plan.subtasks)
        step_results=self.step_execute.run(plan_step,user_contest)
        summary=self.result_summarizer.summarize(query,decomposition_plan,step_results)
        report=self.report_generat.peport_generat(summary)
        return report