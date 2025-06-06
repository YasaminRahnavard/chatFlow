import { useState, useEffect, useRef } from 'react';
import {
  ChakraProvider,
  Box,
  Flex,
  VStack,
  HStack,
  Text,
  Button,
  Textarea,
  Avatar,
  Badge,
  Divider,
  Spinner,
  Card,
  CardBody,
  CardHeader,
  IconButton,
  useColorModeValue,
  useBreakpointValue,
  Drawer,
  DrawerBody,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useDisclosure,
  Container,
  Heading,
  Stack,
  SimpleGrid,
  Icon,
  useToast
} from '@chakra-ui/react';
import {
  ChatIcon,
  AddIcon,
  HamburgerIcon,
  ArrowForwardIcon,
  CheckCircleIcon
} from '@chakra-ui/icons';
import {
  FaRocket,
  FaRobot,
  FaUser,
  FaDocker,
  FaReact,
  FaPython,
  FaDatabase,
  FaNetworkWired
} from 'react-icons/fa';

const API_BASE_URL = import.meta.env.REACT_APP_API_URL || 'http://localhost:8003';
const AI_API_URL = import.meta.env.REACT_APP_AI_API_URL || 'http://localhost:8002';
const APP_NAME = import.meta.env.REACT_APP_APP_NAME || 'ChatFlow';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');
  const [userMode, setUserMode] = useState('guest');
  const [isInitialized, setIsInitialized] = useState(false);
  const messagesEndRef = useRef(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Responsive values
  const sidebarWidth = useBreakpointValue({ base: '100%', md: '300px' });
  const showMobileDrawer = useBreakpointValue({ base: true, md: false });
  const messagePadding = useBreakpointValue({ base: 4, md: 6 });
  const headerHeight = useBreakpointValue({ base: '60px', md: '80px' });

  // Color mode values
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const sidebarBg = useColorModeValue('white', 'gray.800');
  const messageBg = useColorModeValue('white', 'gray.700');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    setUserMode('guest');
    setUsername('Guest User');
    setIsAuthenticated(true);
    await fetchConversations();
    setIsInitialized(true);
  };

  const fetchConversations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/conversations/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setConversations(data.results || data);
        
        if ((data.results || data).length === 0) {
          await createWelcomeConversation();
        }
      } else {
        await createWelcomeConversation();
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
      await createWelcomeConversation();
    }
  };

  const createWelcomeConversation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/conversations/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'Welcome to ChatFlow'
        }),
      });

      if (response.ok) {
        const newConv = await response.json();
        setConversations([newConv]);
        setCurrentConversation(newConv);
        
        const welcomeMessage = {
          id: 'welcome-msg',
          content: 'Welcome to ChatFlow! All of your chat history is kept in this session. Every time you open a new session you should start all over again.',
          role: 'assistant',
          created_at: new Date().toISOString()
        };
        setMessages([welcomeMessage]);
      }
    } catch (error) {
      console.error('Error creating welcome conversation:', error);
      const demoConv = {
        id: 'demo-1',
        title: 'Welcome to ChatFlow',
        updated_at: new Date().toISOString(),
        message_count: 1
      };
      setConversations([demoConv]);
      setCurrentConversation(demoConv);
      
      const welcomeMessage = {
        id: 'welcome-msg',
        content: 'Welcome to ChatFlow! All of your chat history is kept in this session. Every time you open a new session you should start all over again.',
        role: 'assistant',
        created_at: new Date().toISOString()
      };
      setMessages([welcomeMessage]);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/conversations/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: 'Untitled Chat'
        }),
      });

      if (response.ok) {
        const newConv = await response.json();
        setConversations([newConv, ...conversations]);
        setCurrentConversation(newConv);
        setMessages([]);
        onClose(); // Close mobile drawer
      }
    } catch (error) {
      console.error('Error creating conversation:', error);
      const newConv = {
        id: Date.now().toString(),
        title: 'Untitled Chat',
        updated_at: new Date().toISOString(),
        message_count: 0
      };
      setConversations([newConv, ...conversations]);
      setCurrentConversation(newConv);
      setMessages([]);
      onClose();
    }
  };

  const selectConversation = async (conversation) => {
    setCurrentConversation(conversation);
    await fetchMessages(conversation.id);
    onClose(); // Close mobile drawer
  };

  const fetchMessages = async (conversationId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/conversations/${conversationId}/messages/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(data.results || data);
      } else {
        setMessages([]);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
      setMessages([]);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      content: newMessage,
      role: 'user',
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    const messageToSend = newMessage;
    const isFirstMessage = messages.length === 0 || (messages.length === 1 && messages[0].id === 'welcome-msg');
    setNewMessage('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/conversations/chat/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: messageToSend,
          conversation_id: currentConversation?.id
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Generate title from first message (limit to 50 characters)
        const generateTitle = (message) => {
          const cleanMessage = message.trim();
          if (cleanMessage.length <= 50) {
            return cleanMessage;
          }
          return cleanMessage.substring(0, 47) + '...';
        };

        // Handle conversation creation/update
        if (data.conversation_id) {
          const newTitle = isFirstMessage ? generateTitle(messageToSend) : currentConversation?.title;
          
          if (!currentConversation || currentConversation.id !== data.conversation_id) {
            // New conversation created by backend
            const newConv = {
              id: data.conversation_id,
              title: newTitle,
              updated_at: new Date().toISOString(),
              message_count: 2
            };
            setCurrentConversation(newConv);
            setConversations(prev => [newConv, ...prev]);
          } else if (isFirstMessage && currentConversation) {
            // Update existing conversation title with first message
            const updatedConv = {
              ...currentConversation,
              title: newTitle,
              updated_at: new Date().toISOString(),
              message_count: (currentConversation.message_count || 0) + 2
            };
            setCurrentConversation(updatedConv);
            setConversations(prev => 
              prev.map(conv => 
                conv.id === currentConversation.id ? updatedConv : conv
              )
            );
          }
        }
        
        if (data.assistant_message) {
          const assistantMessage = {
            id: data.assistant_message.id,
            content: data.assistant_message.content,
            role: 'assistant',
            created_at: data.assistant_message.created_at
          };
          setMessages(prev => [...prev, assistantMessage]);
        }
      } else {
        const errorMessage = {
          id: Date.now().toString() + '_error',
          content: 'Sorry, I encountered an error. Please try again.',
          role: 'assistant',
          created_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, errorMessage]);
        toast({
          title: "Error",
          description: "Failed to send message. Please try again.",
          status: "error",
          duration: 3000,
          isClosable: true,
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now().toString() + '_error',
        content: 'Sorry, I encountered a connection error. Please try again.',
        role: 'assistant',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      toast({
        title: "Connection Error",
        description: "Please check your connection and try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const Sidebar = () => (
    <VStack spacing={0} h="100vh" bg={sidebarBg} borderRight="1px" borderColor="gray.200">
      {/* Header */}
      <Box w="100%" p={6} borderBottom="1px" borderColor="gray.200">
        <HStack spacing={3} mb={4}>
          <Icon as={FaRocket} color="brand.500" boxSize={6} />
          <Heading size="md" color="brand.600">{APP_NAME}</Heading>
        </HStack>
        <Button
          leftIcon={<AddIcon />}
          colorScheme="brand"
          variant="solid"
          size="sm"
          w="100%"
          onClick={createNewConversation}
          _hover={{ transform: 'translateY(-1px)', boxShadow: 'lg' }}
          transition="all 0.2s"
        >
          New Chat
        </Button>
      </Box>

      {/* Conversations List */}
      <VStack spacing={2} flex={1} w="100%" p={4} overflowY="auto">
        {conversations.map(conv => (
          <Card
            key={conv.id}
            w="100%"
            cursor="pointer"
            onClick={() => selectConversation(conv)}
            bg={currentConversation?.id === conv.id ? 'brand.50' : 'transparent'}
            borderColor={currentConversation?.id === conv.id ? 'brand.200' : 'gray.200'}
            _hover={{ 
              bg: currentConversation?.id === conv.id ? 'brand.100' : 'gray.50',
              transform: 'translateX(2px)',
              transition: 'all 0.2s'
            }}
            size="sm"
          >
            <CardBody p={3}>
              <Text fontWeight="semibold" fontSize="sm" mb={1} noOfLines={1}>
                {conv.title}
              </Text>
              <HStack justifyContent="space-between">
                <Badge colorScheme="gray" size="xs">
                  {conv.message_count || 0} messages
                </Badge>
                <Text fontSize="xs" color="gray.500">
                  {new Date(conv.updated_at).toLocaleDateString()}
                </Text>
              </HStack>
            </CardBody>
          </Card>
        ))}
      </VStack>

      {/* User Info Footer */}
      <Box w="100%" p={4} borderTop="1px" borderColor="gray.200">
        <HStack spacing={3} mb={3}>
          <Avatar size="sm" icon={<FaUser />} bg="brand.500" />
          <VStack spacing={0} align="start" flex={1}>
            <Text fontWeight="medium" fontSize="sm">{username}</Text>
            <Badge colorScheme="green" size="xs">{userMode} mode</Badge>
          </VStack>
        </HStack>
        {userMode === 'guest' && (
          <Box p={3} bg="blue.50" borderRadius="md" borderLeft="4px" borderColor="blue.400">
            <Text fontSize="xs" color="blue.700">
              💡 Chat history saved for this session
            </Text>
          </Box>
        )}
      </Box>
    </VStack>
  );

  const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';
    return (
      <Flex justify={isUser ? 'flex-end' : 'flex-start'} mb={4}>
        <HStack spacing={3} maxW="70%" align="flex-end">
          {!isUser && (
            <Avatar size="sm" icon={<FaRobot />} bg="purple.500" />
          )}
          <Box
            bg={isUser ? 'brand.500' : messageBg}
            color={isUser ? 'white' : 'gray.800'}
            p={3}
            borderRadius="xl"
            borderBottomLeftRadius={isUser ? 'xl' : 'md'}
            borderBottomRightRadius={isUser ? 'md' : 'xl'}
            boxShadow="sm"
            border={!isUser ? '1px' : 'none'}
            borderColor="gray.200"
          >
            <Text fontSize="sm" lineHeight="1.5">{message.content}</Text>
            <Text fontSize="xs" opacity={0.7} mt={1}>
              {new Date(message.created_at).toLocaleTimeString()}
            </Text>
          </Box>
          {isUser && (
            <Avatar size="sm" icon={<FaUser />} bg="brand.500" />
          )}
        </HStack>
      </Flex>
    );
  };

  const TypingIndicator = () => (
    <Flex justify="flex-start" mb={4}>
      <HStack spacing={3} align="flex-end">
        <Avatar size="sm" icon={<FaRobot />} bg="purple.500" />
        <Box
          bg={messageBg}
          p={3}
          borderRadius="xl"
          borderBottomLeftRadius="md"
          boxShadow="sm"
          border="1px"
          borderColor="gray.200"
        >
          <HStack spacing={1}>
            <Spinner size="xs" />
            <Text fontSize="sm" color="gray.500">AI is typing...</Text>
          </HStack>
        </Box>
      </HStack>
    </Flex>
  );

  const WelcomeScreen = () => (
    <Container maxW="2xl" centerContent p={8}>
      <VStack spacing={8} textAlign="center">
        <Box>
          <HStack justify="center" mb={4}>
            <Icon as={FaRocket} boxSize={12} color="brand.500" />
          </HStack>
          <Heading size="2xl" mb={4} bgGradient="linear(to-r, brand.500, purple.500)" bgClip="text">
            Welcome to {APP_NAME}
          </Heading>
          <Text fontSize="lg" color="gray.600" maxW="md">
            A comprehensive Docker-based chat platform showcasing modern cloud computing concepts
          </Text>
        </Box>

        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="100%">
          <VStack spacing={4}>
            <Icon as={FaDocker} boxSize={8} color="blue.500" />
            <Text fontWeight="semibold">Multi-container Docker architecture</Text>
          </VStack>
          <VStack spacing={4}>
            <Icon as={FaReact} boxSize={8} color="cyan.500" />
            <Text fontWeight="semibold">React frontend with Chakra UI</Text>
          </VStack>
          <VStack spacing={4}>
            <Icon as={FaPython} boxSize={8} color="green.500" />
            <Text fontWeight="semibold">Django REST API backend</Text>
          </VStack>
          <VStack spacing={4}>
            <Icon as={FaRobot} boxSize={8} color="purple.500" />
            <Text fontWeight="semibold">FastAPI AI service with Gemini</Text>
          </VStack>
          <VStack spacing={4}>
            <Icon as={FaDatabase} boxSize={8} color="orange.500" />
            <Text fontWeight="semibold">PostgreSQL + Redis</Text>
          </VStack>
          <VStack spacing={4}>
            <Icon as={FaNetworkWired} boxSize={8} color="teal.500" />
            <Text fontWeight="semibold">Custom Docker networks</Text>
          </VStack>
        </SimpleGrid>

        <Button
          size="lg"
          colorScheme="brand"
          rightIcon={<ArrowForwardIcon />}
          onClick={createNewConversation}
          _hover={{ transform: 'translateY(-2px)', boxShadow: 'xl' }}
          transition="all 0.2s"
        >
          Start Your First Chat
        </Button>
      </VStack>
    </Container>
  );

  if (!isInitialized) {
    return (
      <Flex h="100vh" align="center" justify="center" bg={bgColor}>
        <VStack spacing={6}>
          <Icon as={FaRocket} boxSize={16} color="brand.500" />
          <Spinner size="xl" color="brand.500" thickness="4px" />
          <Text fontSize="xl" fontWeight="semibold">{APP_NAME}</Text>
          <Text color="gray.600">Loading...</Text>
        </VStack>
      </Flex>
    );
  }

  if (!isAuthenticated) {
    return (
      <Flex h="100vh" align="center" justify="center" bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
        <Card maxW="md" w="100%" mx={4}>
          <CardHeader textAlign="center" pb={2}>
            <Icon as={FaRocket} boxSize={16} color="brand.500" mb={4} />
            <Heading size="xl" mb={2}>{APP_NAME}</Heading>
            <Text color="gray.600">A Docker-powered chat platform with AI integration</Text>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              <Button
                size="lg"
                colorScheme="brand"
                w="100%"
                onClick={() => {
                  setUserMode('guest');
                  setUsername('Guest User');
                  setIsAuthenticated(true);
                }}
              >
                Continue as Guest
              </Button>
              <Text fontSize="sm" color="gray.500">or</Text>
              <Button
                size="lg"
                variant="outline"
                colorScheme="brand"
                w="100%"
                onClick={() => {
                  setUserMode('authenticated');
                  setUsername('Demo User');
                  setIsAuthenticated(true);
                }}
              >
                Demo Login
              </Button>
            </VStack>
            
            <Divider my={6} />
            
            <VStack spacing={3} textAlign="center">
              <HStack justify="center" spacing={6}>
                <VStack spacing={1}>
                  <CheckCircleIcon color="green.500" />
                  <Text fontSize="xs">No registration required</Text>
                </VStack>
                <VStack spacing={1}>
                  <ChatIcon color="blue.500" />
                  <Text fontSize="xs">Session-based history</Text>
                </VStack>
                <VStack spacing={1}>
                  <Icon as={FaRobot} color="purple.500" />
                  <Text fontSize="xs">AI-powered</Text>
                </VStack>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      </Flex>
    );
  }

  return (
    <Flex h="100vh" bg={bgColor}>
      {/* Desktop Sidebar */}
      {!showMobileDrawer && (
        <Box w={sidebarWidth} flexShrink={0}>
          <Sidebar />
        </Box>
      )}

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="sm">
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <Sidebar />
        </DrawerContent>
      </Drawer>

      {/* Main Content */}
      <Flex flex={1} direction="column" minW={0}>
        {/* Header */}
        <Box
          h={headerHeight}
          px={messagePadding}
          py={4}
          bg={sidebarBg}
          borderBottom="1px"
          borderColor="gray.200"
          boxShadow="sm"
        >
          <Flex align="center" justify="space-between" h="100%">
            <HStack spacing={4}>
              {showMobileDrawer && (
                <IconButton
                  icon={<HamburgerIcon />}
                  variant="ghost"
                  onClick={onOpen}
                  aria-label="Open menu"
                />
              )}
              <VStack spacing={0} align="start">
                <Heading size="md">{currentConversation?.title || 'ChatFlow'}</Heading>
                <HStack spacing={2}>
                  <Box w={2} h={2} bg="green.400" borderRadius="full" />
                  <Text fontSize="sm" color="gray.600">AI Assistant Online</Text>
                </HStack>
              </VStack>
            </HStack>
          </Flex>
        </Box>

        {/* Messages Area */}
        <Box flex={1} overflowY="auto" p={messagePadding}>
          {currentConversation ? (
            <VStack spacing={0} align="stretch">
              {messages.map(message => (
                <MessageBubble key={message.id} message={message} />
              ))}
              {isLoading && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </VStack>
          ) : (
            <WelcomeScreen />
          )}
        </Box>

        {/* Input Area */}
        {currentConversation && (
          <Box p={messagePadding} bg={sidebarBg} borderTop="1px" borderColor="gray.200">
            <HStack spacing={3}>
              <Textarea
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message... (Press Enter to send)"
                disabled={isLoading}
                resize="none"
                minH="44px"
                maxH="120px"
                bg="white"
                border="2px"
                borderColor="gray.200"
                _focus={{
                  borderColor: 'brand.500',
                  boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)',
                }}
              />
              <IconButton
                icon={isLoading ? <Spinner size="sm" /> : <ArrowForwardIcon />}
                colorScheme="brand"
                onClick={sendMessage}
                disabled={!newMessage.trim() || isLoading}
                size="lg"
                borderRadius="full"
                _hover={{ transform: 'translateY(-1px)', boxShadow: 'lg' }}
                transition="all 0.2s"
                aria-label="Send message"
              />
            </HStack>
          </Box>
        )}
      </Flex>
    </Flex>
  );
}

export default App;
