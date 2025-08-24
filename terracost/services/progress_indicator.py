import time
import threading
import sys
import platform
from typing import Optional

class ProgressIndicator:
    """Provides loading animations and progress indicators"""
    
    def __init__(self, message: str = "Processing..."):
        self.message = message
        self.running = False
        self.thread = None
        # Use Windows-compatible spinner characters
        if platform.system() == "Windows":
            self.spinner_chars = ["|", "/", "-", "\\"]
        else:
            self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_char = 0
        self.start_time = None
        self.elapsed_time = 0
    
    def start(self):
        """Start the progress indicator in a separate thread"""
        if self.running:
            return
        
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, final_message: str = "Done!"):
        """Stop the progress indicator"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        
        # Clear the line and show final message
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        # Use Windows-compatible symbols
        if platform.system() == "Windows":
            sys.stdout.write(f"[OK] {final_message}\n")
        else:
            sys.stdout.write(f"✅ {final_message}\n")
        sys.stdout.flush()
    
    def _animate(self):
        """Animate the spinner with elapsed time"""
        while self.running:
            spinner = self.spinner_chars[self.current_char]
            elapsed = time.time() - self.start_time
            elapsed_str = f"({elapsed:.1f}s)"
            
            # Show elapsed time after 5 seconds
            if elapsed > 5:
                display_message = f"{self.message} {elapsed_str}"
            else:
                display_message = self.message
            
            sys.stdout.write(f'\r{spinner} {display_message}')
            sys.stdout.flush()
            
            self.current_char = (self.current_char + 1) % len(self.spinner_chars)
            time.sleep(0.1)
    
    def update_message(self, new_message: str):
        """Update the progress message"""
        self.message = new_message

class CostCalculationProgress:
    """Specialized progress indicator for cost calculation steps"""
    
    def __init__(self, operation_type="cost_calculation"):
        self.progress = ProgressIndicator()
        self.operation_type = operation_type
        
        # Different step sets for different operations
        if operation_type == "cost_calculation":
            self.steps = [
                "📁 Scanning for Terraform files...",
                "🔍 Processing modules...",
                "📊 Extracting resource information...",
                "🌐 Fetching cloud pricing data...",
                "💰 Calculating cost estimates...",
                "📈 Generating uncertainty analysis..."
            ]
        elif operation_type == "suggest":
            self.steps = [
                "🔍 Analyzing current infrastructure...",
                "📊 Calculating current costs...",
                "🤖 Generating AI suggestions...",
                "💡 Processing optimization ideas...",
                "📋 Compiling recommendations...",
                "✨ Finalizing suggestions..."
            ]
        else:
            self.steps = [
                "⚙️ Processing...",
                "🔄 Working...",
                "📝 Analyzing...",
                "✅ Completing..."
            ]
        
        self.current_step = 0
    
    def start(self):
        """Start the cost calculation progress"""
        self.progress.start()
        self.progress.update_message(self.steps[0])
    
    def next_step(self):
        """Move to the next step"""
        self.current_step += 1
        if self.current_step < len(self.steps):
            self.progress.update_message(self.steps[self.current_step])
    
    def stop(self, success: bool = True):
        """Stop the progress indicator"""
        if success:
            if self.operation_type == "suggest":
                self.progress.stop("AI suggestions generated successfully!")
            else:
                self.progress.stop("Cost estimation completed!")
        else:
            if self.operation_type == "suggest":
                self.progress.stop("AI suggestions generation failed!")
            else:
                self.progress.stop("Cost estimation failed!")

def show_loading_animation(func):
    """Decorator to show loading animation during function execution"""
    def wrapper(*args, **kwargs):
        progress = ProgressIndicator("Processing...")
        progress.start()
        
        try:
            result = func(*args, **kwargs)
            progress.stop("Completed successfully!")
            return result
        except Exception as e:
            progress.stop(f"Failed: {str(e)}")
            raise
    
    return wrapper
