import { NextRequest } from "next/server";
import { authenticatedGateway } from "@/lib/gateway";

export async function GET(request: NextRequest) {
  return authenticatedGateway(request);
}

export async function POST(request: NextRequest) {
  return authenticatedGateway(request);
}

export async function PUT(request: NextRequest) {
  return authenticatedGateway(request);
}

export async function PATCH(request: NextRequest) {
  return authenticatedGateway(request);
}

export async function DELETE(request: NextRequest) {
  return authenticatedGateway(request);
}
