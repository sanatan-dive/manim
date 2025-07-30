import { SignedIn, SignedOut,  SignInButton, UserButton,  } from "@clerk/clerk-react"
import { Link } from "react-router-dom"


function Header() {
  
  return (
    <div className=' fixed inset-0 z-10 '>
        <div className='flex justify-around items-center'>
      <div className='font-funnel flex items-center gap-1 m-4 cursor-pointer '>
        <div className='w-4 h-4 bg-black border rounded-full translate-y-0.5 '></div>
        <h1 className='text-xl font-medium'>Madio</h1>
      </div>


      <div className='font-funnel flex items-center gap-4 m-4'>

        <Link to="/create" className='text-sm hover:text-stone-500 duration-200 cursor-pointer'>
          Create
          </Link>
        <span className='text-sm hover:text-stone-500 duration-200 cursor-pointer'>
          Motive
        </span>
        <span className='text-sm hover:text-stone-500 duration-200 cursor-pointer'>Works</span>
        
          
          
      </div>
      <div>
        
        <SignedOut>
          <button className='bg-black text-white font-funnel m-4 px-4 py-2 text-md rounded-full hover:bg-black/80 duration-200 cursor-pointer'>
          <SignInButton />
          </button>
        </SignedOut>
        
        <SignedIn>
          <div className='m-4 flex items-center justify-center '>
          <UserButton />
          </div>
          
        </SignedIn>
        
        
      </div>
      </div>
    </div>
  )
}

export default Header