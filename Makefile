.PHONY: dev dev-backend dev-frontend

dev:
	@echo "Starting backend on :8000 and frontend on :3000"
	@bash -c "cd backend && uvicorn backend.main:app --reload --port 8000" & \
	bash -c "cd frontend && npm run dev" & \
	wait

dev-backend:
	cd backend && uvicorn backend.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev
