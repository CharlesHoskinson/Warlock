-- A caller-held shell owns an offered socket; correlation is not authentication.
module Warlock.Protocol.Ingress
 (IngressOwner,IngressBinding,ingressBinding,CounterError(..),Direction(..),Reason(..),GateStatus(..),
  Priority(..),ChannelError(..),EndpointState(..),Phase(..),OwnerStatus(..),OfferResult(..),ActivationResult(..),IngressResult(..),
  newIngressOwner,transferSocket,activateIngress,receiveIngress,enqueueIngress,sendIngress,retainedIngressFrames,retireIngress,ingressStatus,ingressRejections) where
import Warlock.Protocol.Ingress.Internal
