import time
import threading
import sys
import platform
from typing import Optional

class SuggestProgressIndicator:
    """
    Specialized progress indicator for AI suggestion generation
    Provides detailed feedback for each step of the process
    """
    
    def __init__(self):
        self.running = False
        self.thread = None
        self.current_step = 0
        self.total_steps = 4
        
        # Use Windows-compatible symbols
        if platform.system() == "Windows":
            self.symbols = {
                "analyzing": "[ANALYZE]",
                "calculating": "[CALC]",
                "generating": "[AI-PREP]",
                "processing": "[PROCESS]"
            }
        else:
            self.symbols = {
                "analyzing": "🔍",
                "calculating": "📊",
                "generating": "🤖",
                "processing": "💡"
            }
        
        self.steps = [
            ("analyzing", "Analyzing current infrastructure..."),
            ("calculating", "Calculating current costs..."),
            ("generating", "Preparing AI analysis..."),
            ("processing", "Processing optimization ideas...")
        ]
        
        self.start_time = None
        self.elapsed_time = 0
    
    def start(self):
        """Start the progress indicator"""
        if self.running:
            return
        
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
        
        # Show initial step
        self._show_step(0)
    
    def next_step(self):
        """Move to the next step"""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1
            self._show_step(self.current_step)
    
    def _show_step(self, step_index: int):
        """Display the current step with symbol and message"""
        if step_index < len(self.steps):
            step_type, message = self.steps[step_index]
            symbol = self.symbols.get(step_type, "⚙️")
            
            # Clear line and show step
            sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
            sys.stdout.write(f"{symbol} {message}")
            sys.stdout.flush()
    
    def _animate(self):
        """Animate the progress indicator"""
        while self.running:
            if self.start_time:
                elapsed = time.time() - self.start_time
                elapsed_str = f" ({elapsed:.1f}s)"
                
                # Show elapsed time after 3 seconds
                if elapsed > 3:
                    # Update the current step display with elapsed time
                    if self.current_step < len(self.steps):
                        step_type, message = self.steps[self.current_step]
                        symbol = self.symbols.get(step_type, "⚙️")
                        
                        sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
                        sys.stdout.write(f"{symbol} {message}{elapsed_str}")
                        sys.stdout.flush()
            
            time.sleep(0.5)
    
    def stop(self, success: bool = True):
        """Stop the progress indicator"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        
        # Clear the line silently - no success/failure message
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        sys.stdout.flush()
    
    def update_message(self, message: str):
        """Update the current step message"""
        if self.current_step < len(self.steps):
            step_type, _ = self.steps[self.current_step]
            symbol = self.symbols.get(step_type, "⚙️")
            
            sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
            sys.stdout.write(f"{symbol} {message}")
            sys.stdout.flush()
    
    def show_detail(self, detail: str):
        """Show additional detail below the current step"""
        # Move to next line and show detail
        sys.stdout.write(f"\n   📝 {detail}\n")
        sys.stdout.flush()
        
        # Redraw current step
        self._show_step(self.current_step)

class SuggestStepTracker:
    """
    Tracks progress through the suggestion generation process
    Provides detailed feedback for each phase
    """
    
    def __init__(self):
        self.progress = SuggestProgressIndicator()
        self.current_phase = "initialization"
        self.phase_details = []
    
    def start_analysis(self):
        """Start the infrastructure analysis phase"""
        self.progress.start()
        self.current_phase = "analysis"
        self.phase_details = []
    
    def infrastructure_parsed(self, file_count: int, resource_count: int):
        """Report infrastructure parsing completion"""
        self.progress.next_step()
        detail = f"Found {file_count} Terraform files with {resource_count} resources"
        self.progress.show_detail(detail)
        self.phase_details.append(detail)
    
    def cost_calculation_started(self):
        """Report cost calculation start"""
        self.progress.next_step()
        self.current_phase = "cost_calculation"
    
    def provider_costs_calculated(self, provider: str, resource_count: int, total_cost: float):
        """Report costs calculated for a specific provider"""
        detail = f"{provider.upper()}: {resource_count} resources = ${total_cost:.2f}/month"
        self.progress.show_detail(detail)
        self.phase_details.append(detail)
    
    def ai_generation_started(self):
        """Report AI suggestion generation start"""
        self.progress.next_step()
        self.current_phase = "ai_generation"
    
    def ai_suggestion_generated(self, suggestion_type: str, description: str):
        """Report an AI suggestion being generated"""
        detail = f"Generated {suggestion_type}: {description}"
        self.progress.show_detail(detail)
        self.phase_details.append(detail)
    
    def optimization_processing(self):
        """Report optimization processing start"""
        self.progress.next_step()
        self.current_phase = "optimization"
    
    def complete(self, success: bool = True):
        """Complete the suggestion generation process"""
        self.progress.stop(success)
        return {
            "success": success,
            "phases": self.phase_details
        }
