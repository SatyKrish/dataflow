#!/bin/bash
# Multi-Agent Research System Startup Script

set -e

echo "=== Multi-Agent Research System Startup ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if PostgreSQL is running
check_postgres() {
    print_status "Checking PostgreSQL connection..."
    if command -v psql >/dev/null 2>&1; then
        if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
            print_success "PostgreSQL is running"
            return 0
        else
            print_warning "PostgreSQL is not responding on localhost:5432"
            return 1
        fi
    else
        print_warning "psql command not found - cannot check PostgreSQL"
        return 1
    fi
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    cd data
    if python init_db.py; then
        print_success "Database initialized successfully"
        cd ..
        return 0
    else
        print_error "Database initialization failed"
        cd ..
        return 1
    fi
}

# Start individual services
start_demo_mcp() {
    print_status "Starting Demo MCP Server..."
    cd mcp/demo
    python server.py &
    DEMO_PID=$!
    echo $DEMO_PID > ../../.demo_pid
    cd ../..
    print_success "Demo MCP Server started (PID: $DEMO_PID)"
}

start_denodo_mcp() {
    print_status "Starting Denodo MCP Server..."
    cd mcp/denodo
    python server.py &
    DENODO_PID=$!
    echo $DENODO_PID > ../../.denodo_pid
    cd ../..
    print_success "Denodo MCP Server started (PID: $DENODO_PID)"
}

start_agent_server() {
    print_status "Starting Agent Server..."
    cd agent
    python server.py &
    AGENT_PID=$!
    echo $AGENT_PID > ../.agent_pid
    cd ..
    print_success "Agent Server started (PID: $AGENT_PID)"
}

start_mcp_agent() {
    print_status "Starting MCP Agent Server..."
    cd mcp/agent
    python server.py &
    MCP_AGENT_PID=$!
    echo $MCP_AGENT_PID > ../../.mcp_agent_pid
    cd ../..
    print_success "MCP Agent Server started (PID: $MCP_AGENT_PID)"
}

# Stop all services
stop_services() {
    print_status "Stopping all services..."
    
    # Stop MCP Agent Server
    if [ -f .mcp_agent_pid ]; then
        MCP_AGENT_PID=$(cat .mcp_agent_pid)
        if kill -0 $MCP_AGENT_PID 2>/dev/null; then
            kill $MCP_AGENT_PID
            print_success "Stopped MCP Agent Server (PID: $MCP_AGENT_PID)"
        fi
        rm .mcp_agent_pid
    fi
    
    # Stop Agent Server
    if [ -f .agent_pid ]; then
        AGENT_PID=$(cat .agent_pid)
        if kill -0 $AGENT_PID 2>/dev/null; then
            kill $AGENT_PID
            print_success "Stopped Agent Server (PID: $AGENT_PID)"
        fi
        rm .agent_pid
    fi
    
    # Stop Denodo MCP Server
    if [ -f .denodo_pid ]; then
        DENODO_PID=$(cat .denodo_pid)
        if kill -0 $DENODO_PID 2>/dev/null; then
            kill $DENODO_PID
            print_success "Stopped Denodo MCP Server (PID: $DENODO_PID)"
        fi
        rm .denodo_pid
    fi
    
    # Stop Demo MCP Server
    if [ -f .demo_pid ]; then
        DEMO_PID=$(cat .demo_pid)
        if kill -0 $DEMO_PID 2>/dev/null; then
            kill $DEMO_PID
            print_success "Stopped Demo MCP Server (PID: $DEMO_PID)"
        fi
        rm .demo_pid
    fi
}

# Check service health
check_services() {
    print_status "Checking service health..."
    
    # Check Demo MCP
    if curl -s http://localhost:8080/health >/dev/null 2>&1; then
        print_success "Demo MCP Server: healthy (port 8080)"
    else
        print_warning "Demo MCP Server: not responding (port 8080)"
    fi
    
    # Check Denodo MCP
    if curl -s http://localhost:8081/health >/dev/null 2>&1; then
        print_success "Denodo MCP Server: healthy (port 8081)"
    else
        print_warning "Denodo MCP Server: not responding (port 8081)"
    fi
    
    # Check Agent Server
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        print_success "Agent Server: healthy (port 8001)"
    else
        print_warning "Agent Server: not responding (port 8001)"
    fi
    
    # Check MCP Agent Server
    if curl -s http://localhost:8082/health >/dev/null 2>&1; then
        print_success "MCP Agent Server: healthy (port 8082)"
    else
        print_warning "MCP Agent Server: not responding (port 8082)"
    fi
}

# Main function
main() {
    case "${1:-start}" in
        "start")
            print_status "Starting Multi-Agent Research System..."
            
            # Check PostgreSQL
            if ! check_postgres; then
                print_error "PostgreSQL is not available. Please start PostgreSQL first."
                exit 1
            fi
            
            # Initialize database
            if ! init_database; then
                print_error "Database initialization failed. Please check your configuration."
                exit 1
            fi
            
            # Start services with delays
            start_demo_mcp
            sleep 2
            
            start_denodo_mcp
            sleep 2
            
            start_agent_server
            sleep 3
            
            start_mcp_agent
            sleep 2
            
            print_success "All services started successfully!"
            echo
            print_status "Service URLs:"
            echo "  Demo MCP Server:      http://localhost:8080"
            echo "  Denodo MCP Server:    http://localhost:8081"
            echo "  Agent Server:         http://localhost:8001"
            echo "  MCP Agent Server:     http://localhost:8082"
            echo
            print_status "Use 'bash start_agents.sh stop' to stop all services"
            print_status "Use 'bash start_agents.sh status' to check service health"
            ;;
            
        "stop")
            stop_services
            print_success "All services stopped"
            ;;
            
        "restart")
            stop_services
            sleep 2
            main start
            ;;
            
        "status")
            check_services
            ;;
            
        "help"|"--help"|"-h")
            echo "Multi-Agent Research System Startup Script"
            echo
            echo "Usage: bash start_agents.sh [command]"
            echo
            echo "Commands:"
            echo "  start    Start all services (default)"
            echo "  stop     Stop all services"
            echo "  restart  Restart all services"
            echo "  status   Check service health"
            echo "  help     Show this help message"
            echo
            echo "Services:"
            echo "  - Demo MCP Server (port 8080)"
            echo "  - Denodo MCP Server (port 8081)"
            echo "  - Agent Server (port 8001)"
            echo "  - MCP Agent Server (port 8082)"
            echo
            echo "Prerequisites:"
            echo "  - PostgreSQL running on localhost:5432"
            echo "  - Python dependencies installed in all directories"
            echo "  - Environment variables configured"
            ;;
            
        *)
            print_error "Unknown command: $1"
            echo "Use 'bash start_agents.sh help' for usage information"
            exit 1
            ;;
    esac
}

# Handle Ctrl+C
trap 'echo; print_status "Caught interrupt signal, stopping services..."; stop_services; exit 0' INT

# Run main function
main "$@" 